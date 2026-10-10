import customtkinter
import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import os
import json
from datetime import datetime, date

# --- Import the session manager ---
try:
    from session_manager import active_session
except ImportError:
    class MockSession:
        def get_user_file(self, name): return name

        def get_user(self): return "Admin"

        def set_user(self, name): pass


    active_session = MockSession()

# Configuration
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")


# Class to store and manage appointment records
class AppointmentRecord:
    def __init__(self, pet_name, pet_age, vet, visit_date, visit_time, remark, index=None):
        self.pet_name = pet_name
        self.pet_age = pet_age
        self.vet = vet
        self.visit_date = visit_date
        self.visit_time = visit_time
        self.remark = remark
        self.index = index

    def get_summary(self):
        return (
            f"🐾 {self.pet_name} ({self.pet_age})\n"
            f"📅 {self.visit_date} @ {self.visit_time}\n"
            f"👨‍⚕️ {self.vet}"
        )

    def to_dict(self):
        return {
            "pet_name": self.pet_name,
            "pet_age": self.pet_age,
            "vet": self.vet,
            "visit_date": self.visit_date,
            "visit_time": self.visit_time,
            "remark": self.remark
        }

    @staticmethod
    def from_dict(data):
        return AppointmentRecord(
            data["pet_name"],
            data["pet_age"],
            data["vet"],
            data["visit_date"],
            data["visit_time"],
            data["remark"]
        )


# Widget for displaying an individual record
class RecordCard(customtkinter.CTkFrame):
    def __init__(self, master, record_data, edit_callback, delete_callback, **kwargs):
        super().__init__(master, **kwargs, fg_color="#FFDAB9", corner_radius=8)
        self.record_data = record_data
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure((1, 2, 3), weight=0)

        summary_label = customtkinter.CTkLabel(
            self,
            text=record_data.get_summary(),
            text_color="#4F2222",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor="w",
            justify="left"
        )
        summary_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Store button as an attribute to access its coordinates later
        self.details_button = customtkinter.CTkButton(
            self, text="Remarks", command=self.show_details, width=60, fg_color="#FFA500", hover_color="#E09500"
        )
        self.details_button.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="e")

        edit_button = customtkinter.CTkButton(
            self, text="Edit", command=lambda: self.edit_callback(self.record_data), width=50, fg_color="#4F2222",
            hover_color="#3A1919"
        )
        edit_button.grid(row=0, column=2, padx=(5, 0), pady=5, sticky="e")

        delete_button = customtkinter.CTkButton(
            self, text="🗑️", command=lambda: self.delete_callback(self.record_data), width=40, fg_color="#FF4500",
            hover_color="#CC3800", text_color="white"
        )
        delete_button.grid(row=0, column=3, padx=(5, 10), pady=5, sticky="e")

    def show_details(self):
        win_w, win_h = 350, 250
        x = self.details_button.winfo_rootx()
        y = self.details_button.winfo_rooty() - win_h - 10

        if hasattr(self, 'details_window') and self.details_window.winfo_exists():
            self.details_window.geometry(f"+{x}+{y}")
            self.details_window.lift()
            self.details_window.focus_force()
            return

        self.details_window = customtkinter.CTkToplevel(self)
        self.details_window.title(f"Remark for {self.record_data.pet_name}")
        self.details_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.details_window.resizable(False, False)

        # Force window to front
        self.details_window.lift()
        self.details_window.attributes("-topmost", True)
        self.details_window.after(100, lambda: self.details_window.attributes("-topmost", False))
        self.details_window.focus_force()

        remark_text = customtkinter.CTkTextbox(self.details_window, wrap="word", fg_color="#FFDAB9",
                                               text_color="#4F2222")
        remark_text.insert("1.0", self.record_data.remark)
        remark_text.configure(state="disabled")
        remark_text.pack(padx=20, pady=20, fill="both", expand=True)


# Main Application Class
class VetAppointmentApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.user_filename = active_session.get_user_file("vet_appointments.txt")
        self.current_username = active_session.get_user()

        self.title(f"Vet Appointment - {self.current_username}")
        self.geometry("1280x800")
        self.state("zoomed")
        self.resizable(True, True)

        self.records = []
        self.available_vets = ["Dr. Lim", "Dr. Jones", "Dr. Lee"]
        self.editing_record_index = None

        self.available_times = [f"{h:02d}:{m:02d}" for h in range(9, 23) for m in (0, 30)]
        self.available_times = [t for t in self.available_times if t < "23:00"]

        self.load_records()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.return_to_main)

        self.return_button = customtkinter.CTkButton(
            master=self, text="< ", command=self.return_to_main, width=100, height=50,
            fg_color="transparent", text_color="#4F2222", hover_color="#F0F0F0",
            font=customtkinter.CTkFont(size=30, weight="bold")
        )
        self.return_button.place(x=30, y=30)

        customtkinter.CTkLabel(
            master=self, text="Vet Appointment", font=customtkinter.CTkFont(family="Impact", size=65),
            text_color="#4F2222",
        ).grid(row=0, column=0, columnspan=2, pady=(30, 10), sticky="n")

        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, columnspan=2, padx=50, pady=(0, 50), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1, minsize=450)
        content_frame.grid_columnconfigure(1, weight=1, minsize=450)
        content_frame.grid_rowconfigure(0, weight=1)

        self.record_frame = customtkinter.CTkFrame(content_frame, fg_color="#FFA500", corner_radius=10)
        self.record_frame.grid(row=0, column=0, padx=(0, 25), sticky="nsew")
        self.record_frame.grid_columnconfigure(0, weight=1)
        self.record_frame.grid_rowconfigure(1, weight=1)

        customtkinter.CTkLabel(
            self.record_frame, text="Record", fg_color="#FFD700", text_color="#4F2222",
            font=customtkinter.CTkFont(size=20, weight="bold"), corner_radius=6, anchor="center"
        ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="ew")

        self.scrollable_records = customtkinter.CTkScrollableFrame(
            self.record_frame, fg_color="#FFA500", label_text="Saved Appointments",
            label_font=customtkinter.CTkFont(size=16, weight="bold"), label_text_color="#4F2222",
        )
        self.scrollable_records.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scrollable_records.grid_columnconfigure(0, weight=1)

        self.input_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        self.input_frame.grid(row=0, column=1, padx=(25, 0), sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=0)
        self.input_frame.grid_columnconfigure(1, weight=1)

        self.create_input_widgets()
        self.refresh_record_display()

    def reclaim_focus(self):
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

    def load_records(self):
        if os.path.exists(self.user_filename):
            try:
                with open(self.user_filename, 'r') as f:
                    data_list = json.load(f)
                    self.records = [AppointmentRecord.from_dict(d) for d in data_list]
            except Exception:
                self.records = []
        else:
            self.records = []

    def save_records(self):
        try:
            data_list = [record.to_dict() for record in self.records]
            with open(self.user_filename, 'w') as f:
                json.dump(data_list, f, indent=4)
        except Exception as e:
            messagebox.showerror("Saving Error", f"Error: {e}")
            self.reclaim_focus()

    def return_to_main(self):
        self.save_records()
        self.destroy()

    def create_input_widgets(self):
        r = 0

        def create_input_row(label_text, row_num, widget_type="entry", options=None, command=None):
            customtkinter.CTkLabel(
                self.input_frame, text=f"{label_text} :", text_color="#4F2222",
                font=customtkinter.CTkFont(size=18, weight="bold"), anchor="e"
            ).grid(row=row_num, column=0, padx=(0, 10), pady=10, sticky="e")

            if widget_type == "entry":
                widget = customtkinter.CTkEntry(self.input_frame, fg_color="#F0F0F0", text_color="#4F2222", height=35)
                if command: widget.bind("<Button-1>", command)
            elif widget_type == "optionmenu":
                widget = customtkinter.CTkOptionMenu(
                    self.input_frame, values=options if options else ["Select..."], fg_color="#F0F0F0", height=35,
                    button_color="#E0E0E0", button_hover_color="#D0D0D0", text_color="#4F2222"
                )
            widget.grid(row=row_num, column=1, pady=10, sticky="ew")
            return widget

        self.petname_entry = create_input_row("Pet Name", r, "entry")
        r += 1

        self.petage_entry = create_input_row("Pet Age", r, "entry")
        vcmd = (self.register(lambda S, P: (S.isdigit() or S == "") and len(P) <= 2), '%S', '%P')
        self.petage_entry.configure(validate="key", validatecommand=vcmd)
        r += 1

        self.vet_option = create_input_row("Vet", r, "optionmenu", self.available_vets)
        r += 1

        self.visitdate_entry = create_input_row("Visit Date", r, "entry", command=self.show_calendar)
        self.visitdate_entry.insert(0, "Click to select date")
        self.visitdate_entry.configure(state="readonly")
        r += 1

        self.visittime_option = create_input_row("Visit Time", r, "optionmenu", self.available_times)
        r += 1

        customtkinter.CTkLabel(
            self.input_frame, text="Remark :", text_color="#4F2222",
            font=customtkinter.CTkFont(size=18, weight="bold"), anchor="e"
        ).grid(row=r, column=0, padx=(0, 10), pady=(10, 5), sticky="ne")

        self.remark_textbox = customtkinter.CTkTextbox(self.input_frame, fg_color="#F0F0F0", text_color="#4F2222",
                                                       height=145, wrap="word")
        self.remark_textbox.grid(row=r, column=1, pady=(10, 5), sticky="ew")
        r += 1

        self.save_button = customtkinter.CTkButton(
            self.input_frame, text="Save Appointment", command=self.save_or_update_appointment,
            font=customtkinter.CTkFont(size=20, weight="bold"), fg_color="#4F2222", hover_color="#3A1919", height=45
        )
        self.save_button.grid(row=r, column=1, pady=(20, 0), sticky="ew")

    def show_calendar(self, event=None):
        cal_win = tk.Toplevel(self)
        cal_win.title("Select Date")

        x = self.visitdate_entry.winfo_rootx()
        y = self.visitdate_entry.winfo_rooty() + self.visitdate_entry.winfo_height()
        cal_win.geometry(f"+{x}+{y}")

        cal_win.transient(self)
        cal_win.grab_set()

        cal = Calendar(cal_win, selectmode='day', date_pattern='yyyy-mm-dd', mindate=date.today())
        cal.pack(pady=10, padx=10)

        def confirm_date():
            self.visitdate_entry.configure(state="normal")
            self.visitdate_entry.delete(0, "end")
            self.visitdate_entry.insert(0, cal.get_date())
            self.visitdate_entry.configure(state="readonly")
            cal_win.destroy()

        customtkinter.CTkButton(cal_win, text="Select", command=confirm_date, fg_color="#4F2222").pack(pady=(0, 10))

    def refresh_record_display(self):
        for widget in self.scrollable_records.winfo_children(): widget.destroy()
        if not self.records:
            customtkinter.CTkLabel(self.scrollable_records, text="No records saved yet.", text_color="#4F2222",
                                   font=customtkinter.CTkFont(size=14, slant="italic")).pack(pady=40, padx=20)
            return
        for i, record in enumerate(self.records):
            record.index = i
            RecordCard(self.scrollable_records, record_data=record, edit_callback=self.load_record_for_editing,
                       delete_callback=self.delete_record).pack(fill="x", padx=10, pady=(10, 0))

    def load_record_for_editing(self, record_data):
        self.editing_record_index = record_data.index
        self.save_button.configure(text="Update Appointment")
        self.clear_inputs()
        self.petname_entry.insert(0, record_data.pet_name)
        self.petage_entry.insert(0, record_data.pet_age)
        self.vet_option.set(record_data.vet)
        self.visittime_option.set(record_data.visit_time)
        self.visitdate_entry.configure(state="normal")
        self.visitdate_entry.delete(0, "end")
        self.visitdate_entry.insert(0, record_data.visit_date)
        self.visitdate_entry.configure(state="readonly")
        self.remark_textbox.insert("1.0", record_data.remark)

    def save_or_update_appointment(self):
        date_input = self.visitdate_entry.get()
        if date_input == "Click to select date":
            messagebox.showerror("Input Error", "Please select a Visit Date.")
            self.reclaim_focus()
            return

        pet_name = self.petname_entry.get().strip()
        pet_age = self.petage_entry.get().strip()
        vet = self.vet_option.get()
        visit_date = date_input
        visit_time = self.visittime_option.get()
        remark = self.remark_textbox.get("1.0", "end-1c").strip()

        if not all([pet_name, pet_age, vet, visit_date, visit_time, remark]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            self.reclaim_focus()
            return

        try:
            selected_dt = datetime.strptime(f"{visit_date} {visit_time}", "%Y-%m-%d %H:%M")
            if selected_dt < datetime.now():
                messagebox.showerror("Date/Time Error", "You cannot book an appointment at the past!Please select a new time.")
                self.reclaim_focus()
                return
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date/time selection.")
            self.reclaim_focus()
            return

        new_data = AppointmentRecord(pet_name, pet_age, vet, visit_date, visit_time, remark)
        if self.editing_record_index is not None:
            self.records[self.editing_record_index] = new_data
            self.editing_record_index = None
        else:
            self.records.append(new_data)

        self.refresh_record_display()
        self.clear_inputs()
        self.save_records()

    def delete_record(self, record_data):
        if messagebox.askyesno("Confirm Delete", f"Delete appointment for {record_data.pet_name}?"):
            if self.editing_record_index == record_data.index:
                self.editing_record_index = None
                self.clear_inputs()
            del self.records[record_data.index]
            self.refresh_record_display()
            self.save_records()
        self.reclaim_focus()

    def clear_inputs(self):
        self.petname_entry.delete(0, "end")
        self.petage_entry.delete(0, "end")
        self.visitdate_entry.configure(state="normal")
        self.visitdate_entry.delete(0, "end")
        self.visitdate_entry.insert(0, "Click to select date")
        self.visitdate_entry.configure(state="readonly")
        self.remark_textbox.delete("1.0", "end")
        if self.editing_record_index is None: self.save_button.configure(text="Save Appointment")


if __name__ == "__main__":
    try:
        active_session.set_user("Admin")
    except:
        pass
    app = VetAppointmentApp()
    app.mainloop()