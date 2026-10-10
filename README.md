# SimYenYue_TanYunNI_TeoYanQi
DCS1S2G2 Daily Paws Pet Care Assistant  
# DailyPaws Pet Care Assistant

# 1.Introduction
DailyPaws Pet Care Assistant App is designed to assist the pet owners manage
daily care routines and important events for their loving pets. It provides a
centralized platform to track feeding times, vet appointments, and grooming schedules for their pets.

# 2.Objectives
-Simplify pet care management for busy owners with tkinter and  customtkinter advanced GUI design.
-Provide logs in each system for essential activities with tkcalender.
-Maintain records of pet health and grooming history by using json and txt file.
-Enhance organization and reduce stress in pet care routines.


# 3.Compiler
-PyCharm 2025.2.4

# 4. library file required
-Python 3.10+
-tkinter                #Styling and UI design
-customtkinter  # Modern Styling and UI design
-pillow(PIL)  # For manipulating the image
-json file     # Data storage
-os  # To verify file paths and data availability
-datetime # track current date and time
-deepcopy  # user for data preservation
-tkcalender #to select date month year

# 5. System Features
-Authentication System: Secure Login and Logout functionality to protect pet data and user settings.
-Main Dashboard: A central landing page providing an overview of recent activities and quick access to all trackers.
-Feeding Tracker: Logs specific feeding times to remind user to feed their pet with specific amount of food types
-Grooming Management: Tracks and edit grooming history and schedules upcoming hygiene sessions.
-Vet Appointment Tracker: Maintains a record of health checkups, vaccinations, and medical history.
-Overall Schedule Page: A specialized view to identify conflicting tasks or dense schedules, ensuring no appointment is missed.

# 6. Project Structure
│
├─pet_login.py: The entry point of the application. Handles user validation and redirects to the main interface.
│
├─session_manager.py: Manages the current user state and login persistence throughout the application.
│
├─Mainpage.py: The central navigation hub that connects the user to all specific pet care modules.
│
├─feeding.py: UI and logic for tracking meal times, portions, and food types.
│
├─grooming.py: Manages hygiene schedules and history for the pet's well-being.
│
├─overall_schedule.py: Aggregates data from all trackers into a single "at-a-glance" view to prevent over-scheduling.
│
├─schedule_manager.py: Contains the backend logic for saving, loading, and updating pet schedules using JSON.
│
├─username_json : store user input data for each session
│
├─username_txt: store user input data for each session
│
├─png:image


# 7. How to run the application

## Step 1: Download the libries to required to run the application
bash
pip install customtkinter pillow tkcalendar

## Step 2: Run the application
bash
python pet_login.py

# 8. Data Storage
-json
-txt

# 9. Learning Outcome
- Project file linking
- GUI design with tkinter and customtkinter
- adding moving Gif in the main page

# 10. Conclusion
DailyPaws is an open-source tool created to simplify the lives of pet owners.
Pet owners can keep track their pet overall well-being by using our app.
