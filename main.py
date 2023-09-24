import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from pygame import mixer
from datetime import datetime
from time import sleep, strftime
from threading import Thread
import json

# Store alarm times and messages in separate dictionaries
upcoming_alarms = {}
past_alarms = {}

# Create a dictionary to store alarm labels
alarm_labels = {}

def load_data(file_name="data.json"):
    global upcoming_alarms, past_alarms, alarm_labels
    try:
        with open(file_name, "r") as json_file:
            data = json.load(json_file)
            # Check if the data contains 'upcoming_alarms' and 'past_alarms' keys
            if 'upcoming_alarms' in data:
                upcoming_alarms.update(data['upcoming_alarms'])
            if 'past_alarms' in data:
                past_alarms.update(data['past_alarms'])
            if 'alarm_labels' in data:
                alarm_labels.update(data['alarm_labels'])
            # Convert string keys back to tuples
            upcoming_alarms = {tuple(key.split(',')): value for key, value in upcoming_alarms.items()}
            past_alarms = {tuple(key.split(',')): value for key, value in past_alarms.items()}
            alarm_labels = {tuple(key.split(',')): value for key, value in alarm_labels.items()}
    except FileNotFoundError:
        print(f"File '{file_name}' not found. Initializing with empty dictionaries.")

def save_data(file_name="data.json"):
    global upcoming_alarms, past_alarms, alarm_labels
    # Convert tuple keys to strings before saving
    upcoming_alarms_str_keys = {','.join(map(str, key)): value for key, value in upcoming_alarms.items()}
    past_alarms_str_keys = {','.join(map(str, key)): value for key, value in past_alarms.items()}
    alarm_labels_str_keys = {','.join(map(str, key)): value for key, value in alarm_labels.items()}
    
    data = {
        'upcoming_alarms': upcoming_alarms_str_keys,
        'past_alarms': past_alarms_str_keys,
        'alarm_labels': alarm_labels_str_keys
    }
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)

load_data()

# Colors
bg_color = "#ffffff"
green_color = "#4CAF50"  # Green color

# Create the main window
window = tk.Tk()

program_active = True

window.title("Alarm Clock")
window.geometry('800x400')  # Larger window to accommodate the clock display
window.configure(bg=bg_color)

# Frame setup
frame_line = tk.Frame(window, width=800, height=5, bg=green_color)
frame_line.grid(row=0, column=0)

frame_body = tk.Frame(window, width=800, height=290, bg=bg_color)
frame_body.grid(row=1, column=0)

# Configure frame body
img = Image.open("alarm_icon.png")
img = img.resize((100, 100))
img = ImageTk.PhotoImage(img)

app_image = tk.Label(frame_body, height=100, image=img, bg=bg_color)
app_image.place(x=10, y=10)

name = tk.Label(frame_body, text="Alarm", height=1, font=("Arial 18 bold"), bg=bg_color)
name.place(x=125, y=10)

# Text input for customized alarm message
message_label = tk.Label(frame_body, text="Custom Message:", height=1, font=("Arial 10 bold"), bg=bg_color, fg=green_color)
message_label.place(x=10, y=130)

custom_message = tk.Entry(frame_body, width=30, font=("Arial 12"))
custom_message.place(x=140, y=130)

# Add a label input field in your user interface
label_label = tk.Label(frame_body, text="Alarm Label:", height=1, font=("Arial 10 bold"), bg=bg_color, fg=green_color)
label_label.place(x=10, y=160)

label_entry = tk.Entry(frame_body, width=30, font=("Arial 12"))
label_entry.place(x=140, y=160)


hour_label = tk.Label(frame_body, text="Hour", height=1, font=("Arial 10 bold"), bg=bg_color, fg=green_color)
hour_label.place(x=127, y=40)
c_hour = ttk.Combobox(frame_body, width=2, font=("Arial 15"))
c_hour['values'] = tuple(f"{i:02d}" for i in range(24))  # 24-hour format
c_hour.current(0)
c_hour.place(x=130, y=58)

min_label = tk.Label(frame_body, text="Min", height=1, font=("Arial 10 bold"), bg=bg_color, fg=green_color)
min_label.place(x=177, y=40)
c_min = ttk.Combobox(frame_body, width=2, font=("Arial 15"))
c_min['values'] = tuple(f"{i:02d}" for i in range(60))
c_min.current(0)
c_min.place(x=180, y=58)

sec_label = tk.Label(frame_body, text="Sec", height=1, font=("Arial 10 bold"), bg=bg_color, fg=green_color)
sec_label.place(x=227, y=40)
c_sec = ttk.Combobox(frame_body, width=2, font=("Arial 15"))
c_sec['values'] = tuple(f"{i:02d}" for i in range(60))
c_sec.current(0)
c_sec.place(x=230, y=58)

alarm_active = False

# Function to activate the alarm
def activate_alarm():
    global t, alarm_active
    alarm_hour = c_hour.get()
    alarm_min = c_min.get()
    alarm_sec = c_sec.get()
    message = custom_message.get()
    label = label_entry.get()
    if message:
        alarm_time = (alarm_hour, alarm_min, alarm_sec)
        upcoming_alarms[alarm_time] = message
    else:
        alarm_time = (alarm_hour, alarm_min, alarm_sec)
        upcoming_alarms[alarm_time] = f"Alarm {len(upcoming_alarms)+1+len(past_alarms)}"

    if label:
        alarm_labels[alarm_time] = label
    else:
        alarm_labels[alarm_time] = "No Label"
    save_data()

    # Set alarm_active to True
    alarm_active = True

    t = Thread(target=alarm)
    t.start()

# Create the Deactivate button, but initially hide it
deactivate_button = tk.Button(frame_body, font=('Arial 10 bold'), text='Deactivate', bg=bg_color)
deactivate_button.place(x=187, y=95)
deactivate_button.place_forget()

def deactivate_alarm():
    global deactivate_button, alarm_active
    print("Deactivated alarm")
    mixer.music.stop()
     # Set alarm_active to False
    alarm_active = False
    
    deactivate_button.place_forget()

activate_button = tk.Button(frame_body, font=('Arial 10 bold'), text='Activate', bg=bg_color, command=activate_alarm)
activate_button.place(x=125, y=95)

# Create the Deactivate button, but initially hide it
deactivate_button = tk.Button(frame_body, font=('Arial 10 bold'), text='Deactivate', bg=bg_color, command=deactivate_alarm)
deactivate_button.place(x=187, y=95)
deactivate_button.place_forget()


def sound_alarm(message):
    global deactivate_button, alarm_active
    mixer.music.load('alarm_sound.wav')
    mixer.music.play()
    print("Custom Message:", message)

    if alarm_active:
        deactivate_button = tk.Button(frame_body, font=('Arial 10 bold'), text='Deactivate', bg=bg_color, command=deactivate_alarm)
        deactivate_button.place(x=187, y=95)
    else:  
        deactivate_button.place_forget()

    # Set alarm_active to True when the alarm is triggered
    alarm_active = True


def alarm():
    while True:
        now = datetime.now()

        current_hour = now.strftime("%H")
        current_min = now.strftime("%M")
        current_sec = now.strftime("%S")
        for alarm_time, alarm_message in upcoming_alarms.items():
            if alarm_time == (current_hour, current_min, current_sec):
                print("Time to take a break!")
                sound_alarm(alarm_message)
                past_alarms[alarm_time] = alarm_message
                try:
                    del upcoming_alarms[alarm_time]
                except KeyError:
                    pass
                save_data()
                break
        sleep(1)

mixer.init()

# Create a frame for the clock display
frame_clock = tk.Frame(window, width=200, height=100, bg=bg_color)
frame_clock.place(x=450, y=10)

# Clock type variable
clock_type = tk.StringVar()
clock_type.set("Digital")  # Default: Digital Clock


# Function to update the clock display
def update_clock():
    current_time = strftime("%H:%M:%S")  # Format: HH:MM:SS

    if clock_type.get() == "Digital":
        clock_label.config(text=current_time, font=("Arial 14 bold"))
    elif clock_type.get() == "Analog":
        # Implement Analog Clock rendering here (hour, minute, second hands)
        pass

    window.after(1000, update_clock)  # Update every 1 second

# Create a label for the digital clock
clock_label = tk.Label(frame_clock, text="", font=("Arial 14 bold"), bg=bg_color)
clock_label.pack(pady=20)

"""
# # Function to toggle between Digital and Analog clocks
# def toggle_clock():
#     if clock_type.get() == "Digital":
#         clock_type.set("Analog")
#     else:
#         clock_type.set("Digital")

# # Create a button to toggle between Digital and Analog clocks
# toggle_button = tk.Button(frame_clock, text="Toggle Clock", command=toggle_clock)
# toggle_button.pack()

"""

# Create frames for displaying upcoming and past alarms
frame_upcoming_alarms = tk.Frame(window, width=300, height=200, bg=bg_color)
frame_upcoming_alarms.place(x=20, y=200)

frame_past_alarms = tk.Frame(window, width=300, height=200, bg=bg_color)
frame_past_alarms.place(x=340, y=200)

# Labels to display upcoming and past alarms
upcoming_alarms_label = tk.Label(frame_upcoming_alarms, text="Upcoming Alarms", font=("Arial 12 bold"), bg=bg_color)
upcoming_alarms_label.pack(pady=10)

past_alarms_label = tk.Label(frame_past_alarms, text="Past Alarms", font=("Arial 12 bold"), bg=bg_color)
past_alarms_label.pack(pady=10)

# Listboxes to display upcoming and past alarms
upcoming_alarms_listbox = tk.Listbox(frame_upcoming_alarms, width=25, height=6, font=("Arial 10"))
upcoming_alarms_listbox.pack()

past_alarms_listbox = tk.Listbox(frame_past_alarms, width=25, height=6, font=("Arial 10"))
past_alarms_listbox.pack()

# Function to update the list of upcoming alarms
def update_upcoming_alarms():
    upcoming_alarms_listbox.delete(0, tk.END)  # Clear the list

    for alarm_time, alarm_message in upcoming_alarms.items():
        formatted_time = f"{alarm_time[0]}:{alarm_time[1]}:{alarm_time[2]}"
        label = alarm_labels.get(alarm_time, "")  # Get associated label
        
        upcoming_alarms_listbox.insert(tk.END, f"{label} @ {formatted_time} - {alarm_message}")

    window.after(1000, update_upcoming_alarms)  # Update every 10 seconds


# Function to update the list of past alarms
def update_past_alarms():
    past_alarms_listbox.delete(0, tk.END)  # Clear the list

    for alarm_time, alarm_message in past_alarms.items():
        formatted_time = f"{alarm_time[0]}:{alarm_time[1]}:{alarm_time[2]}"
        label = alarm_labels.get(alarm_time, "")  # Get associated label
        
        past_alarms_listbox.insert(tk.END, f"{label} @ {formatted_time} - {alarm_message}")

    window.after(1000, update_past_alarms)  # Update every 5 seconds

# Uncomplete Feature: Countdown Timer
"""
# Create a frame for the countdown timer
frame_countdown = tk.Frame(window, width=200, height=100, bg=bg_color)
frame_countdown.place(x=450, y=130)

countdown_label = tk.Label(frame_countdown, text="Countdown Timer", font=("Arial 12 bold"), bg=bg_color)
countdown_label.pack()

# Text input fields for hours, minutes, and seconds
countdown_hours_label = tk.Label(frame_countdown, text="Hours:", font=("Arial 10 bold"), bg=bg_color, fg=green_color)
countdown_hours_label.pack()
countdown_hours_entry = tk.Entry(frame_countdown, width=5, font=("Arial 10"))
countdown_hours_entry.pack()

countdown_minutes_label = tk.Label(frame_countdown, text="Minutes:", font=("Arial 10 bold"), bg=bg_color, fg=green_color)
countdown_minutes_label.pack()
countdown_minutes_entry = tk.Entry(frame_countdown, width=5, font=("Arial 10"))
countdown_minutes_entry.pack()

countdown_seconds_label = tk.Label(frame_countdown, text="Seconds:", font=("Arial 10 bold"), bg=bg_color, fg=green_color)
countdown_seconds_label.pack()
countdown_seconds_entry = tk.Entry(frame_countdown, width=5, font=("Arial 10"))
countdown_seconds_entry.pack()

countdown_active = False
countdown_duration = 0

def start_countdown():
    global countdown_active, countdown_duration
    if not countdown_active:
        hours = int(countdown_hours_entry.get())
        minutes = int(countdown_minutes_entry.get())
        seconds = int(countdown_seconds_entry.get())
        countdown_duration = hours * 3600 + minutes * 60 + seconds
        countdown_active = True
        countdown()

def countdown():
    global countdown_active, countdown_duration
    while countdown_duration > 0 and countdown_active:
        hours, remainder = divmod(countdown_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_display.config(text=f"Time Left: {hours:02d}:{minutes:02d}:{seconds:02d}")
        countdown_duration -= 1
        sleep(1)
    countdown_active = False
    countdown_display.config(text="Countdown Complete")


# Button to start the countdown
start_countdown_button = tk.Button(frame_countdown, text="Start Countdown", font=('Arial 10 bold'), bg=bg_color, command=start_countdown)
start_countdown_button.pack()

def pause_countdown():
    global countdown_active
    countdown_active = False

def stop_countdown():
    global countdown_active, countdown_duration
    countdown_active = False
    countdown_duration = 0
    countdown_display.config(text="Countdown Stopped")

pause_countdown_button = tk.Button(frame_countdown, text="Pause Countdown", font=('Arial 10 bold'), bg=bg_color, command=pause_countdown)
pause_countdown_button.pack()

stop_countdown_button = tk.Button(frame_countdown, text="Stop Countdown", font=('Arial 10 bold'), bg=bg_color, command=stop_countdown)
stop_countdown_button.pack()

countdown_display = tk.Label(frame_countdown, text="", font=("Arial 14 bold"), bg=bg_color)
countdown_display.pack()
"""

# Start updating the clock, upcoming alarms, and past alarms
update_clock()
update_upcoming_alarms()
update_past_alarms()

window.mainloop()


program_active = False