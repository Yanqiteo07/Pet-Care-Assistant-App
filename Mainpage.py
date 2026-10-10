import customtkinter
import tkinter.messagebox
from PIL import Image, ImageTk, ImageSequence
import os
import tkinter as tk
from feeding import open_feeding_tracker
from grooming import open_grooming_page
from Vet import VetAppointmentApp
from overall_schedule import OverallSchedulePage

customtkinter.set_appearance_mode("Light")
MAIN_BG_COLOR = "#EEEEEE"

# --- CORE POSITIONING CONSTANTS ---
TITLE_Y_POS = 630  # Y-position for the title baseline
TITLE_X_POS = 50  # X-position for the title left edge

# Estimates
TITLE_HEIGHT_ESTIMATE = 60  #  "DAILY PAW" label
CAT_WIDTH = 100  # GIF width

# Calculates the cat's vertical position so it is centered beside the title text.
CAT_WALK_Y = TITLE_Y_POS - (TITLE_HEIGHT_ESTIMATE / 2) + (CAT_WIDTH / 2)
BUTTON_FRAME_RELY = 0.35


WALK_MIN_X = 0
WALK_MAX_X = 1080


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("DAILY PAWS")
        self.state("zoomed")
        self.resizable(True, True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.overall_schedule_window = None


        # GIF
        self.gif_path = "cat-8915.gif"
        self.gif_label = None
        self.frames_right = []
        self.frames_left = []
        self.current_frame = 0
        self.frame_delay = 50
        self.gif_width = CAT_WIDTH
        self.walk_step = 5

        self.x_position = 0
        self.direction = 1

        self.ensure_gif_file_exists()
        self.load_gif_frames()

        self.show_main_page()


    def ensure_gif_file_exists(self):
        if not os.path.exists(self.gif_path):
            print(f"\n[CRITICAL WARNING] Required GIF file '{self.gif_path}' not found.")
            print("Attempting to create a temporary static image placeholder.")
            try:
                img = Image.new('RGB', (self.gif_width, 100), color='blue')
                img.save(self.gif_path)
                print(f"Successfully created '{self.gif_path}' placeholder. App will run but not animate correctly.")
            except Exception as e:
                print(f"Could not create placeholder GIF: {e}")

    def load_gif_frames(self):

        try:
            img = Image.open(self.gif_path)
            for frame in ImageSequence.Iterator(img):
                frame_resized = frame.resize((self.gif_width, 100), Image.Resampling.LANCZOS)
                self.frames_right.append(ImageTk.PhotoImage(frame_resized))
                frame_flipped = frame_resized.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                self.frames_left.append(ImageTk.PhotoImage(frame_flipped))
        except Exception as e:
            print(f"Error loading GIF frames: {e}")
            if not self.frames_right:
                self.frames_right.append(ImageTk.PhotoImage(Image.new("RGB", (self.gif_width, 100), "blue")))
                self.frames_left.append(ImageTk.PhotoImage(Image.new("RGB", (self.gif_width, 100), "blue")))


    def animate_gif(self):
        # --- Modified for placement---
        current_frames_set = self.frames_right if self.direction == 1 else self.frames_left
        if not current_frames_set:
            return

        self.current_frame = (self.current_frame + 1) % len(current_frames_set)
        frame_image = current_frames_set[self.current_frame]

        self.gif_label.configure(image=frame_image)
        self.gif_label.image = frame_image

        window_width = self.winfo_width()
        self.x_position += self.direction * self.walk_step

        new_direction = self.direction

        # Cat walks across the entire window width
        if self.x_position + self.gif_width >= window_width:
            new_direction = -1
            self.x_position = window_width - self.gif_width
        elif self.x_position <= 0:
            new_direction = 1
            self.x_position = 0

        if new_direction != self.direction:
            self.direction = new_direction
            self.current_frame = 0

        # IMPORTANT: Using CAT_WALK_Y for vertical placement
        self.gif_label.place(x=self.x_position, y=CAT_WALK_Y, anchor="sw")

        self.after(self.frame_delay, self.animate_gif)



    def logout_event(self):
            if tkinter.messagebox.askokcancel(
                    "Logout Confirmation",
                    "Are you sure you want to log out of DAILY PAWS?",
                    parent=self
            ):

                self.destroy()

    def overall_schedule_event(self):
        # Check if the window is open or was closed previously
        if self.overall_schedule_window is None or not self.overall_schedule_window.winfo_exists():
            self.overall_schedule_window = OverallSchedulePage(self)
        else:

            self.overall_schedule_window.focus()


    def grooming_event(self):
        open_grooming_page()

    def vet_event(self):
        vet_window = VetAppointmentApp()
        vet_window.mainloop()

    def feeding_event(self):
        open_feeding_tracker(self)

    def show_main_page(self):

        self.configure(fg_color=MAIN_BG_COLOR)
        for widget in self.winfo_children():
            widget.destroy()

        # --- Logout Button  ---
        customtkinter.CTkButton(
            master=self, text="Logout", command=self.logout_event,
            width=55, height=55, corner_radius=30, fg_color="#8B4513", hover_color="#A0522D",
            font=customtkinter.CTkFont(size=25, weight="bold")
        ).place(x=30, y=30, anchor="nw")

        # --- Main Buttons Layout Frame  ---
        button_container = customtkinter.CTkFrame(self, fg_color="transparent")
        button_container.place(relx=0.5, rely=BUTTON_FRAME_RELY, anchor=customtkinter.CENTER)

        for i in range(4):
            button_container.grid_columnconfigure(i, weight=1, uniform="group1")

        btn_style = {
            "width": 150, "height": 150, "corner_radius": 20, "fg_color": "#FFB346",
            "text_color": "#4F2222", "font": customtkinter.CTkFont(family="Comic Sans MS", size=18, weight="bold"),
            "hover_color": "#FDF5E6"
        }

        def create_feature_button(master, text, command, row, col):
            customtkinter.CTkButton(
                master=master, text=text.replace(' ', '\n'), command=command, **btn_style
            ).grid(row=row, column=col, padx=30, pady=20)

        create_feature_button(button_container, "Feeding Tracker", self.feeding_event, 0, 0)
        create_feature_button(button_container, "Grooming", self.grooming_event, 0, 1)
        create_feature_button(button_container, "Vet", self.vet_event, 0, 2)
        create_feature_button(button_container, "Overall Schedule", self.overall_schedule_event, 0, 3)

        # --- DAILY PAW Title ---
        customtkinter.CTkLabel(
            master=self,
            text="DAILY PAWS",
            font=customtkinter.CTkFont(family="Impact", size=58),
            text_color="#4F2222",
            fg_color="transparent"
        ).place(x=TITLE_X_POS, y=TITLE_Y_POS, anchor="sw")

        customtkinter.CTkLabel(
            master=self,
            text="for the one you love and care",
            font=customtkinter.CTkFont(family="Georgia", size=18),
            text_color="#4F2222",
            fg_color="transparent"
        ).place(x=TITLE_X_POS, y=TITLE_Y_POS + 35, anchor="sw")

        # --- CAT WALKING (GIF) ---
        self.gif_label = tk.Label(self, bg=MAIN_BG_COLOR)
        self.gif_label.place(x=self.x_position, y=CAT_WALK_Y, anchor="sw")
        self.animate_gif()


if __name__ == "__main__":
    app = App()
    app.mainloop()
