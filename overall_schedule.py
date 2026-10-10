import tkinter as tk
from tkinter import messagebox
from schedule_manager import ScheduleManager
from datetime import datetime
from session_manager import active_session

# UI COLORS(?
MAIN_BG_COLOR = "#EEEEEE"
COLUMN_BG_COLOR = "#FFB346"
CARD_CONTAINER_COLOR = "#FDF5E6"
HEADER_COLOR = "#FFB346"
BUTTON_FG_COLOR = "#4F2222"
GUIDE_TEXT_COLOR = "#666666"


class OverallSchedulePage(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.current_user = active_session.get_user()

        self.title(f"Overall Schedule - {self.current_user}")
        self.geometry("1150x780")
        self.state("zoomed")
        self.configure(bg=MAIN_BG_COLOR)
        self.grab_set()

        self.manager = ScheduleManager()

        self.main_frame = tk.Frame(self, bg=MAIN_BG_COLOR)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_group")
        self.main_frame.grid_rowconfigure(2, weight=1)

        self.setup_header()
        self.setup_columns()
        self.setup_guide()
        self.refresh_ui()

    def setup_header(self):
        header_row_frame = tk.Frame(self.main_frame, bg=MAIN_BG_COLOR)
        header_row_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        header_row_frame.grid_columnconfigure(1, weight=1)

        self.exit_button = tk.Button(
            header_row_frame, text="< ", command=self.exit_page,
            bg=MAIN_BG_COLOR, fg=BUTTON_FG_COLOR, font=('Arial', 30, 'bold'), relief=tk.FLAT
        )
        self.exit_button.grid(row=0, column=0, sticky="w", padx=(0, 20))

        tk.Label(
            header_row_frame, text=f"{self.current_user.upper()}'S OVERALL SCHEDULE",
            font=('Arial', 20, 'bold'), fg=BUTTON_FG_COLOR, bg=MAIN_BG_COLOR
        ).grid(row=0, column=1, sticky="nsew")

        self.undo_button = tk.Button(
            header_row_frame, text=f"🔄 Undo ({self.manager.get_undo_count()})",
            command=self.undo_task_ui, bg=COLUMN_BG_COLOR, fg=BUTTON_FG_COLOR,
            font=('Arial', 15, 'bold'), relief=tk.FLAT
        )
        self.undo_button.grid(row=0, column=2, sticky="e", padx=(0, 20))

        for i, category in enumerate(['feeding', 'grooming', 'vet']):
            tk.Label(
                self.main_frame, text=category.upper(), font=('Arial', 14, 'bold'),
                fg="white", bg=HEADER_COLOR, height=2
            ).grid(row=1, column=i, sticky="new", padx=10, pady=(0, 5))

    def setup_columns(self):
        self.column_frames = {}
        for i, category in enumerate(['feeding', 'grooming', 'vet']):
            container = tk.Frame(self.main_frame, bg=CARD_CONTAINER_COLOR)
            container.grid(row=2, column=i, sticky="nsew", padx=10, pady=5)
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            canvas = tk.Canvas(container, bg=CARD_CONTAINER_COLOR, highlightthickness=0)
            scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg=CARD_CONTAINER_COLOR)

            scroll_frame.bind("<Configure>", lambda e, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            container.bind('<Configure>', lambda e, c=canvas: c.itemconfigure(c.find_all()[0], width=e.width))

            self.column_frames[category] = scroll_frame

    def setup_guide(self):
        guide_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.RIDGE)
        guide_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=(15, 0))

        guide_text = (
            "💡 QUICK GUIDE:\n"
            "• Tap the [ ✔ ] tick button to mark it as COMPLETE and remove it from your daily schedule.\n"
            "• Accidentally completed a task? Use the [ 🔄 Undo ] button at the top right to restore it instantly."
        )

        tk.Label(
            guide_frame,
            text=guide_text,
            font=('Arial', 11, 'italic'),
            fg=GUIDE_TEXT_COLOR,
            bg="white",
            justify="left",
            padx=20,
            pady=10
        ).pack(side="left")

    def get_schedule_data_by_category(self):
        data = self.manager.get_schedule_data()
        all_tasks = []
        for category, task_list in data.items():
            all_tasks.extend(task_list)

        def sort_key(item):
            date_str = item.get('visit_date', item.get('Date'))
            time_str = item.get('visit_time', item.get('time', item.get('Time')))
            try:
                if date_str and time_str: return datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
                return datetime.max
            except ValueError:
                return datetime.max

        all_tasks.sort(key=sort_key)
        grouped_tasks = {'feeding': [], 'grooming': [], 'vet': []}
        for task in all_tasks:
            cat = task.get('category', 'feeding')
            if cat in grouped_tasks: grouped_tasks[cat].append(task)
        return grouped_tasks

    def _populate_tasks(self, frame, tasks, category):
        for widget in frame.winfo_children(): widget.destroy()
        if not tasks:
            tk.Label(frame, text=f"No {category.capitalize()} Tasks!", fg="#777", bg=CARD_CONTAINER_COLOR).pack(pady=50)
            return

        for item in tasks:
            pet_name = item.get('pet_name', item.get('Pet Name', 'N/A'))
            date_val = item.get('visit_date', item.get('Date', 'N/A'))
            time_val = item.get('visit_time', item.get('time', item.get('Time', 'N/A')))

            if category == 'feeding':
                title_text, detail_text = f"Pet: {pet_name}", f"Food: {item.get('task')} | Time: {time_val}"
            elif category == 'grooming':
                title_text, detail_text = f"Pet: {pet_name} | {item.get('task')}", f"Date: {date_val} | Time: {time_val}"
            else:  # Vet
                title_text, detail_text = f"Pet: {pet_name} | Dr. {item.get('vet')}", f"Date: {date_val} | Time: {time_val}"

            card = tk.Frame(frame, bg="white", bd=1, relief=tk.SOLID)
            card.pack(fill="x", padx=10, pady=5, ipady=5)
            card.grid_columnconfigure(0, weight=1)

            tk.Label(card, text=title_text, font=('Arial', 12, 'bold'), bg="white").grid(row=0, column=0, sticky="w",
                                                                                         padx=10)
            tk.Label(card, text=detail_text, font=('Arial', 10), bg="white").grid(row=1, column=0, sticky="w", padx=10)

            tk.Button(card, text="✔", command=lambda cat=category, iid=item['id']: self.complete_task_ui(cat, iid),
                      bg="#4F2222", fg="white", font=('Arial', 10, 'bold')).grid(row=0, column=1, rowspan=2, padx=10)

    def refresh_ui(self):
        grouped_data = self.get_schedule_data_by_category()
        for category, tasks in grouped_data.items():
            if category in self.column_frames: self._populate_tasks(self.column_frames[category], tasks, category)
        self.undo_button.configure(text=f"🔄 Undo ({self.manager.get_undo_count()})")

    def complete_task_ui(self, category, item_id):
        if self.manager.complete_task(category, item_id):
            self.refresh_ui()
            if hasattr(self.master, 'refresh_all_schedules'): self.master.refresh_all_schedules()
        self.lift()

    def undo_task_ui(self):
        if self.manager.undo_last_action():
            self.refresh_ui()
            if hasattr(self.master, 'refresh_all_schedules'): self.master.refresh_all_schedules()
        else:
            messagebox.showinfo("Undo", "No actions to undo.")
        self.lift()

    def exit_page(self):
        self.destroy()