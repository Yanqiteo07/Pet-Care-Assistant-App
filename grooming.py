import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import os
import datetime
# --- Import the session manager ---
from session_manager import active_session

# --- Configuration ---
FONT_SCALE = 1.2
BASE_SIZE = {"normal": 18, "label": 20, "title": 36}

GROOMING_TASKS = [
    "Brushing",
    "Nail Clipping",
    "Ear Care",
    "Bath & Blow-dry"
]

def get_font(kind="normal", bold=False):
    size = int(BASE_SIZE[kind] * FONT_SCALE)
    return "Arial", size, "bold" if bold else "normal"

def bring_to_front(window):
    window.lift()
    window.attributes('-topmost', True)
    window.after(100, lambda: window.attributes('-topmost', False))

def open_grooming_page():
    records_file = active_session.get_user_file("grooming_records.txt")
    current_username = active_session.get_user()

    root = tk.Toplevel()
    root.geometry("1400x900")
    root.state("zoomed")
    root.title(f"Grooming Schedule - {current_username}")
    root.config(bg="#fdf6e3")

    bring_to_front(root)
    root.current_record_index = -1
    style = ttk.Style()
    style.configure("TButton", font=get_font("normal", bold=True), padding=12, background="#FFB346", foreground="black")
    style.configure("Delete.TButton", font=get_font("normal", bold=True), padding=12, background="#FF6347", foreground="black")
    style.configure("TLabel", font=get_font("normal"), background="#fdf6e3")

    # --- Records List---
    left_frame = tk.Frame(root, width=400, bg="#FFB346", relief="ridge", bd=2)
    left_frame.pack(side="left", fill="y")
    left_frame.grid_propagate(False)

    # ---Form ---
    right_frame = tk.Frame(root, bg="#fdf6e3")
    right_frame.pack(side="right", fill="both", expand=True)

    # --- Back Button  ---
    back_button = tk.Button(
        root, text="< ", command=root.destroy,
        bg="#FFB346", fg="#4F2222", font=("Arial", 30, "bold"),
        relief="flat", activebackground="#FFB346", cursor="hand2"
    )
    back_button.place(x=30, y=30)
    back_button.lift()

    # --- Content for Records---
    tk.Label(left_frame, text="📋 Records", font=get_font("label", bold=True), bg="#FFB346").pack(pady=(80, 10))

    record_listbox = tk.Listbox(left_frame, font=get_font("normal"), width=35, height=10,
                                bg="#fdf6e3", fg="#333", selectbackground="#ADD8E6",
                                exportselection=False, highlightthickness=0)
    record_listbox.pack(pady=(0, 10), padx=10)

    tk.Label(left_frame, text="Details:", font=get_font("label", bold=True), bg="#FFB346", fg="#444").pack(pady=(10, 5))
    detail_text = tk.Text(left_frame, font=get_font("normal"), width=35, height=10, bg="#fffaf0",
                          fg="#333", relief="solid", bd=1, wrap="word")
    detail_text.pack(pady=(0, 10), padx=10)

    # --- Data Persistence functions ---
    def get_all_records_from_file():
        if not os.path.exists(records_file): return []
        try:
            with open(records_file, "r", encoding="utf-8") as file:
                return [rec.strip() for rec in file.read().split("-" * 40) if rec.strip()]
        except: return []

    def load_records():
        record_listbox.delete(0, tk.END)
        records = get_all_records_from_file()
        if not records:
            record_listbox.insert(tk.END, "No Record Yet!")
            return
        for rec in records:
            lines = rec.split("\n")
            pet_name = next((l.split(":")[1].strip() for l in lines if l.startswith("Pet Name:")), "Unknown")
            date = next((l.split(":")[1].strip() for l in lines if l.startswith("Date:")), "Unknown")
            record_listbox.insert(tk.END, f"{pet_name} - {date}")

    def clear_form_and_reset():
        submit_button.config(text="Submit")
        root.current_record_index = -1
        record_listbox.selection_clear(0, tk.END)
        pet_name_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        time_entry.set("12:00")
        task_entry.set(GROOMING_TASKS[0])
        detail_text.delete("1.0", tk.END)

    def delete_record():
        selected = record_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record.", parent=root)
            return
        index = selected[0]
        records = get_all_records_from_file()
        if index < len(records) and messagebox.askyesno("Delete", "Delete this record?", parent=root):
            del records[index]
            with open(records_file, "w", encoding="utf-8") as f:
                for r in records: f.write(r + "\n" + "-" * 40 + "\n")
            load_records()
            clear_form_and_reset()

    ttk.Button(left_frame, text="Delete", command=delete_record, style="Delete.TButton").pack(pady=10)

    # --- Form ---
    tk.Label(right_frame, text="🐾 Grooming Schedule", font=get_font("title", bold=True), bg="#fdf6e3", fg="#444").pack(pady=(30, 10))

    form_frame = tk.Frame(right_frame, bg="#fdf6e3")
    form_frame.pack(pady=(20, 20), fill="x", padx=50)
    form_frame.grid_columnconfigure(1, weight=1)

    FORM_WIDTH = 50

    def create_input(label_text, row, widget_type="entry"):
        tk.Label(form_frame, text=label_text + ":", font=get_font("normal"), bg="#fdf6e3", anchor="e", width=15).grid(
            row=row, column=0, padx=10, pady=20, sticky="e")
        if widget_type == "entry":
            entry = ttk.Entry(form_frame, font=get_font("normal"), width=FORM_WIDTH)
        elif widget_type == "date":
            # --- UPDATED: Added mindate to prevent past date selection ---
            entry = DateEntry(form_frame, font=get_font("normal"), width=FORM_WIDTH - 2, background="darkblue",
                              foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd", state="readonly",
                              mindate=datetime.date.today())
        elif widget_type == "time":
            times = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
            entry = ttk.Combobox(form_frame, values=times, font=get_font("normal"), width=FORM_WIDTH - 2, state="readonly")
            entry.set("12:00")
        elif widget_type == "task":
            entry = ttk.Combobox(form_frame, values=GROOMING_TASKS, font=get_font("normal"), width=FORM_WIDTH - 2, state="readonly")
            entry.set(GROOMING_TASKS[0])
        entry.grid(row=row, column=1, padx=10, pady=20, sticky="ew")
        return entry

    pet_name_entry = create_input("Pet Name", 0)
    desc_entry = create_input("Description", 1)
    date_entry = create_input("Date", 2, "date")
    time_entry = create_input("Time", 3, "time")
    task_entry = create_input("Task", 4, "task")

    def on_record_select(event):
        selected = record_listbox.curselection()
        if not selected: return
        index = selected[0]
        records = get_all_records_from_file()
        if index < len(records):
            root.current_record_index = index
            content = records[index]
            detail_text.delete("1.0", tk.END)
            detail_text.insert(tk.END, content)
            data = dict(line.split(":", 1) for line in content.split("\n") if ":" in line)
            pet_name_entry.delete(0, tk.END)
            pet_name_entry.insert(0, data.get("Pet Name", "").strip())
            desc_entry.delete(0, tk.END)
            desc_entry.insert(0, data.get("Description", "").strip())
            # DateEntry update handles past dates gracefully
            date_entry.set_date(data.get("Date", "").strip())
            time_entry.set(data.get("Time", "").strip())
            task_entry.set(data.get("Task", "").strip())
            submit_button.config(text="Update Schedule")

    record_listbox.bind("<<ListboxSelect>>", on_record_select)

    def submit_or_update_schedule():
        data = {
            "Pet Name": pet_name_entry.get().strip(),
            "Description": desc_entry.get().strip(),
            "Date": date_entry.get().strip(),
            "Time": time_entry.get().strip(),
            "Task": task_entry.get().strip()
        }
        if not data["Pet Name"]:
            messagebox.showwarning("Warning", "Enter a Pet Name", parent=root)
            return

        # --- UPDATED: Added Time Validation to prevent past appointments ---
        try:
            selected_dt = datetime.datetime.strptime(f"{data['Date']} {data['Time']}", "%Y-%m-%d %H:%M")
            if selected_dt < datetime.datetime.now():
                messagebox.showerror("Error", "You cannot schedule a grooming session at the past!Please select a new time.", parent=root)
                return
        except ValueError:
            pass

        new_content = "\n".join(f"{k}: {v}" for k, v in data.items())
        records = get_all_records_from_file()
        if root.current_record_index != -1:
            records[root.current_record_index] = new_content
        else:
            records.append(new_content)
        with open(records_file, "w", encoding="utf-8") as f:
            for r in records: f.write(r + "\n" + "-" * 40 + "\n")
        load_records()
        clear_form_and_reset()
        bring_to_front(root)

    submit_button = ttk.Button(right_frame, text="Submit", command=submit_or_update_schedule)
    submit_button.pack(pady=20)
    load_records()

if __name__ == "__main__":
    active_session.set_user("Admin")
    main_root = tk.Tk()
    tk.Button(main_root, text="Open Grooming", command=open_grooming_page).pack(pady=50)
    main_root.mainloop()