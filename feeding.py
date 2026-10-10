import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
import json
import os

try:
    from session_manager import active_session
except ImportError:
    class MockSession:
        def get_user_file(self, name): return name

        def get_user(self): return "Admin"

        def set_user(self, name): pass


    active_session = MockSession()

# Color Palette
DARK_BROWN = "#4F2222"
BROWN = "#8B4513"
LIGHT_BROWN = "#A0522D"
GOLD = "#FFB346"
CREAM = "#FDF5E6"

BASE_FILENAME = "feeding_history.json"

ctk.set_appearance_mode("light")
ctk.set_widget_scaling(1.2)

feeding_window = None


def open_feeding_tracker(master):
    global feeding_window

    user_filename = active_session.get_user_file(BASE_FILENAME)
    current_username = active_session.get_user()

    feeding_window = ctk.CTkToplevel(master)
    feeding_window.title(f"🐾 Feeding Tracker - {current_username}")
    feeding_window.geometry("1150x780")
    feeding_window.state("zoomed")
    feeding_window.configure(fg_color=CREAM)

    feeding_window.transient(master)
    feeding_window.grab_set()
    feeding_window.lift()
    feeding_window.focus_force()

    # BACK BUTTON
    back_btn = ctk.CTkButton(
        master=feeding_window,
        text="< ",
        command=feeding_window.destroy,
        width=100,
        height=50,
        fg_color="transparent",
        text_color=DARK_BROWN,
        hover_color="#F0F0F0",
        font=ctk.CTkFont(size=30, weight="bold")
    )
    back_btn.place(x=30, y=30)

    def validate_age(S, P):
        return (S.isdigit() or S == "") and len(P) <= 2

    vcmd_age = (feeding_window.register(validate_age), '%S', '%P')

    main_frame = ctk.CTkFrame(feeding_window, fg_color=CREAM)
    main_frame.pack(fill="both", expand=True, padx=20, pady=(90, 20))
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=2)

    # Record Side
    left = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=GOLD)
    left.grid(row=0, column=0, sticky="nswe", padx=(0, 15))

    ctk.CTkLabel(left, text="📜 Record", font=("Arial Rounded MT Bold", 23), text_color=DARK_BROWN).pack(pady=12)

    history_frame = ctk.CTkFrame(left, corner_radius=12, fg_color=CREAM)
    history_frame.pack(fill="both", expand=True, padx=10, pady=8)
    history_frame.pack_propagate(False)

    history_list = tk.Listbox(
        history_frame,
        font=("Consolas", 16),
        bg=CREAM,
        fg=DARK_BROWN,
        selectmode=tk.SINGLE,
        relief="flat",
        highlightthickness=0,
        exportselection=False,
        activestyle='none'
    )

    scroll = ttk.Scrollbar(history_frame, command=history_list.yview)
    history_list.configure(yscrollcommand=scroll.set)
    history_list.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=6)
    scroll.pack(side="right", fill="y", padx=(0, 4), pady=6)

    hist_btn_frame = ctk.CTkFrame(left, fg_color="transparent")
    hist_btn_frame.pack(pady=8)

    # Input Side
    right = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=CREAM)
    right.grid(row=0, column=1, sticky="nswe")
    right.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(right, text="Pet & Feeding Info", font=("Arial Rounded MT Bold", 28), text_color=DARK_BROWN).grid(
        row=0, column=0, columnspan=2, pady=(10, 25))

    def input_row(label, row, bg_color=CREAM, text_col=DARK_BROWN, is_age=False):
        ctk.CTkLabel(right, text=label, font=("Arial", 16), text_color=BROWN).grid(row=row, column=0, sticky="e",
                                                                                   padx=(0, 10), pady=10)
        entry = ctk.CTkEntry(
            right, height=38, text_color=text_col, fg_color=bg_color, border_color=BROWN,
            validate="key" if is_age else None,
            validatecommand=vcmd_age if is_age else None
        )
        entry.grid(row=row, column=1, sticky="ew", pady=10)
        return entry

    pet_name_entry = input_row("Pet Name      :", 1, bg_color=CREAM, text_col=BROWN)
    pet_age_entry = input_row("Age               :", 2, is_age=True)

    date_entry = ctk.CTkEntry(right, height=38, text_color=BROWN, fg_color=CREAM, border_color=BROWN)
    ctk.CTkLabel(right, text="Date              :", font=("Arial", 16), text_color=BROWN).grid(row=3, column=0,
                                                                                               sticky="e", padx=(0, 10),
                                                                                               pady=10)
    date_entry.grid(row=3, column=1, sticky="ew", pady=10)
    date_entry.insert(0, str(datetime.date.today()))
    date_entry.configure(state="readonly")

    def open_calendar(event=None):
        cal_win = tk.Toplevel(feeding_window)
        cal_win.title("Select Date")
        cal_win.transient(feeding_window)
        cal_win.grab_set()

        # Position calendar near the entry
        x, y = date_entry.winfo_rootx(), date_entry.winfo_rooty() + date_entry.winfo_height()
        cal_win.geometry(f"+{x}+{y}")

        # REMOVED mindate restriction - allows any date selection
        cal = Calendar(cal_win, date_pattern="yyyy-mm-dd")
        cal.pack(padx=10, pady=10)

        def select_date():
            date_entry.configure(state="normal")
            date_entry.delete(0, tk.END)
            date_entry.insert(0, cal.get_date())
            date_entry.configure(state="readonly")
            cal_win.destroy()

        ctk.CTkButton(cal_win, text="Select", fg_color=BROWN, command=select_date).pack(pady=(0, 10))

    date_entry.bind("<Button-1>", open_calendar)

    # Time Selection
    ctk.CTkLabel(right, text="Time              :", font=("Arial", 16), text_color=BROWN).grid(row=4, column=0,
                                                                                               sticky="e", padx=(0, 10),
                                                                                               pady=10)
    times_list = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    time_box = ctk.CTkComboBox(right, values=times_list, height=38, state="readonly", fg_color=CREAM,
                               border_color=BROWN, button_color=BROWN)
    time_box.grid(row=4, column=1, sticky="ew", pady=10)
    now = datetime.datetime.now()
    time_box.set(f"{now.hour:02d}:{'30' if now.minute >= 30 else '00'}")

    # Food Selection
    ctk.CTkLabel(right, text="Food Type     :", font=("Arial", 16), text_color=BROWN).grid(row=5, column=0, sticky="e",
                                                                                           padx=(0, 10), pady=10)
    food_options = ["Dry Food", "Wet Food", "Snacks", "Milk", "Water"]
    food_box = ctk.CTkComboBox(right, values=food_options, height=38, state="readonly", fg_color=CREAM,
                               button_color=BROWN, border_color=BROWN)
    food_box.grid(row=5, column=1, sticky="ew", pady=10)
    food_box.set(food_options[0])

    # Amount Selection
    ctk.CTkLabel(right, text="Amount (g/ml):", font=("Arial", 16), text_color=BROWN).grid(row=6, column=0, sticky="e",
                                                                                          padx=(0, 10), pady=10)
    amount_values = [str(i) for i in range(35, 111, 5)]
    amount_box = ctk.CTkComboBox(right, values=amount_values, fg_color=CREAM, border_color=BROWN, button_color=BROWN,
                                 text_color=DARK_BROWN, height=38, state="readonly")
    amount_box.grid(row=6, column=1, sticky="ew", pady=10)
    amount_box.set("35")

    # DATA HANDLING
    records = []
    editing_index = None

    def refresh_history():
        history_list.delete(0, tk.END)
        for r in records:
            line = f"{r['Pet Name'].ljust(10)} | {r['Date']} | {r['Time']} | {r['Food Type']}"
            history_list.insert(tk.END, line)

    def add_record():
        nonlocal editing_index
        name = pet_name_entry.get().strip().title()
        if not name:
            messagebox.showerror("Error", "Pet Name is required!", parent=feeding_window)
            return

        # Time validation logic removed to allow past/future recording
        sel_date = date_entry.get()
        sel_time = time_box.get()

        data = {
            "Pet Name": name, "Age": pet_age_entry.get(), "Date": sel_date,
            "Time": sel_time, "Food Type": food_box.get(), "Amount": amount_box.get()
        }

        if editing_index is not None:
            records[editing_index] = data
            editing_index = None
        else:
            records.append(data)

        refresh_history()
        save_json()
        clear_fields()

    def edit_selected():
        nonlocal editing_index
        sel = history_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a record to edit.", parent=feeding_window)
            return

        idx = sel[0]
        r = records[idx]
        editing_index = idx

        pet_name_entry.delete(0, tk.END)
        pet_name_entry.insert(0, r["Pet Name"])
        pet_age_entry.delete(0, tk.END)
        pet_age_entry.insert(0, r["Age"])
        date_entry.configure(state="normal")
        date_entry.delete(0, tk.END)
        date_entry.insert(0, r["Date"])
        date_entry.configure(state="readonly")
        time_box.set(r["Time"])
        food_box.set(r["Food Type"])
        amount_box.set(r["Amount"])

    def delete_selected():
        nonlocal editing_index
        sel = history_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a record to delete.", parent=feeding_window)
            return

        idx = sel[0]
        if messagebox.askyesno("Confirm", "Delete this record?", parent=feeding_window):
            records.pop(idx)
            if editing_index == idx:
                editing_index = None
                clear_fields()
            elif editing_index is not None and editing_index > idx:
                editing_index -= 1
            refresh_history()
            save_json()

    def clear_fields():
        nonlocal editing_index
        editing_index = None
        pet_name_entry.delete(0, tk.END)
        pet_age_entry.delete(0, tk.END)
        now_reset = datetime.datetime.now()
        time_box.set(f"{now_reset.hour:02d}:{'30' if now_reset.minute >= 30 else '00'}")
        food_box.set(food_options[0])
        amount_box.set("35")

    def save_json():
        with open(user_filename, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def load_json():
        if os.path.exists(user_filename):
            try:
                with open(user_filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records.clear()
                    records.extend(data)
            except:
                pass
        refresh_history()

    # Action Buttons
    btn_frame = ctk.CTkFrame(right, fg_color="transparent")
    btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
    ctk.CTkButton(btn_frame, text="Add / Save", width=180, height=42, fg_color=LIGHT_BROWN, command=add_record).grid(
        row=0, column=0, padx=6)
    ctk.CTkButton(btn_frame, text="Clear Fields", width=180, height=42, fg_color=LIGHT_BROWN,
                  command=clear_fields).grid(row=0, column=1, padx=6)

    # Sidebar Buttons
    ctk.CTkButton(hist_btn_frame, text="Edit Selected", command=edit_selected).pack(pady=3)
    ctk.CTkButton(hist_btn_frame, text="Delete Selected", fg_color=BROWN, command=delete_selected).pack(pady=3)
    ctk.CTkButton(hist_btn_frame, text="Clear All", fg_color="#AA3333",
                  command=lambda: [records.clear(), refresh_history(), save_json()] if messagebox.askyesno("Confirm",
                                                                                                           "Clear ALL history?") else None).pack(
        pady=3)

    load_json()


if __name__ == "__main__":
    active_session.set_user("Admin")
    root = ctk.CTk()
    root.title("App Controller")
    ctk.CTkButton(root, text="Open Tracker", command=lambda: open_feeding_tracker(root)).pack(expand=True, padx=50,
                                                                                              pady=50)
    root.mainloop()