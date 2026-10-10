import tkinter as tk
import tkinter.messagebox as messagebox
import json
import os
from PIL import Image, ImageTk
#  Import the session manager ---
from session_manager import active_session

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = "credentials.json"


# Safe credential loading
def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                content = f.read()
                if not content: return {}
                return json.loads(content)
        except Exception:
            return {}
    return {}


def save_credentials(credentials):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f)


stored_credentials = load_credentials()

# Setup Window
window = tk.Tk()
window.state("zoomed")
window.title("DailyPaws")
window.config(background="#EEEEEE")

# --- ICON LOADING ---
try:
    icon_path = os.path.join(SCRIPT_DIR, 'logo.png')
    icon_image = Image.open(icon_path)
    resized_icon = icon_image.resize((64, 64))
    icon_photo = ImageTk.PhotoImage(resized_icon)
    window.iconphoto(True, icon_photo)
    window._icon_ref = icon_photo
except Exception as e:
    print(f"Warning: Icon could not be loaded. {e}")

# --- LOGO LOADING ---
photo = None
try:
    img_path = os.path.join(SCRIPT_DIR, 'pet logo.png')
    photo_image = Image.open(img_path)
    resized_image = photo_image.resize((300, 300))
    photo = ImageTk.PhotoImage(resized_image)
except Exception as e:
    print(f"Warning: Main logo could not be loaded. {e}")

# Label for Logo
label = tk.Label(window,
                 text="Welcome to DailyPaws!",
                 font=('Arial', 40, 'bold'),
                 fg='#4F2222',
                 bg='#EEEEEE',
                 padx=20,
                 pady=20,
                 image=photo,
                 compound='bottom')

if photo is not None:
    label._image_ref = photo
label.pack(pady=20)

# --- Login Frame ---
login_frame = tk.Frame(window, bg="#FFB346")
login_frame.pack(pady=50)

username_label = tk.Label(login_frame, text="Username", bg="#FFF5BD", font=("Arial", 18), width=15)
username_entry = tk.Entry(login_frame, font=("Arial", 18), width=20)
username_feedback = tk.Label(login_frame, text="", fg="red", bg="#FFB346", font=("Arial", 12), width=40)

password_label = tk.Label(login_frame, text="Password", bg="#FFF5BD", font=("Arial", 18), width=15)
password_entry = tk.Entry(login_frame, show="*", font=("Arial", 18), width=20)
password_feedback = tk.Label(login_frame, text="", fg="red", bg="#FFB346", font=("Arial", 12), width=40)


# --- Validation Logic ---
def validate_username():
    username = username_entry.get()
    if username and not username.isupper():
        username_feedback.config(text="⚠ Username must be ALL CAPITAL LETTERS", fg="red")
    elif username:
        username_feedback.config(text="✔ Format valid", fg="green")
    else:
        username_feedback.config(text="")


def validate_password():
    password = password_entry.get()
    if password and (not password.isdigit() or len(password) != 6):
        password_feedback.config(text="⚠ Password must be 6 digits", fg="red")
    elif password:
        password_feedback.config(text="✔ Format valid", fg="green")
    else:
        password_feedback.config(text="")


# --- Logic Separation ---

def login_check():
    username = username_entry.get()
    password = password_entry.get()

    if username in stored_credentials:
        if stored_credentials[username] == password:

            # --- SESSION LOGIC START ---
            active_session.set_user(username)

            window.destroy()
            try:
                from Mainpage import App
                app = App()
                app.mainloop()
            except Exception as e:
                err_root = tk.Tk()
                err_root.withdraw()
                messagebox.showerror("Error", f"Could not load Mainpage: {e}")
                err_root.destroy()
        else:
            messagebox.showerror("Login Error", "Incorrect password.")
    else:
        messagebox.showwarning("Account Not Found", "This username does not exist. Please Sign Up.")


def register_user():
    username = username_entry.get()
    password = password_entry.get()

    # Final validation
    if not username.isupper() or len(password) != 6 or not password.isdigit():
        messagebox.showwarning("Invalid Input", "Ensure username is CAPS and password is 6 digits.")
        return

    if username in stored_credentials:
        messagebox.showinfo("Existing User", "This username is already taken. Try login.")
    else:
        stored_credentials[username] = password
        save_credentials(stored_credentials)
        messagebox.showinfo("Success", "Account created successfully! You can now Login.")


# --- Buttons and Layout ---
username_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
username_entry.grid(row=1, column=1, padx=10, pady=10)
username_feedback.grid(row=2, column=1, sticky="w")

password_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)
password_entry.grid(row=3, column=1, padx=10, pady=10)
password_feedback.grid(row=4, column=1, sticky="w")


button_frame = tk.Frame(login_frame, bg="#FFB346")
button_frame.grid(row=5, column=0, columnspan=2, pady=20)

# --- BUTTON POSITIONS SWAPPED HERE ---

signup_button = tk.Button(button_frame, text="Sign Up", font=("Arial", 18, "bold"),
                          command=register_user, width=10, bg='#EEEEEE', fg='#4F2222')
signup_button.pack(side="left", padx=10)

login_button = tk.Button(button_frame, text="Login", font=("Arial", 18, "bold"),
                         command=login_check, width=10, bg='#EEEEEE', fg='#4F2222')
login_button.pack(side="left", padx=10)


username_entry.bind("<KeyRelease>", lambda e: validate_username())
password_entry.bind("<KeyRelease>", lambda e: validate_password())

window.mainloop()