#run this every time you open the project
#'. .\venv_pythonAuro\Scripts\activate'
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import messagebox
import threading
import sys
import numpy as np
import matplotlib.pyplot as plt
from python_imagesearch import imagesearch
import mss
import pytesseract
from PIL import Image
import cv2

######## Project Flags
enableDebug = False

######## Globals
receiver_email_global = None
log_callback = None  # Pointer to log function
script_running = False  # To avoid multiple runs


def log(msg):
    print(msg)
    if log_callback:
        log_callback(msg)

def find_icon_on_all_monitors(icon_path):
    pos = imagesearch.imagesearch(icon_path, 0.6)
    if pos[0] != -1:
        return True
    return False

def grab_ScreenShot():
    with mss.mss() as sct:
        sct.save()

def get_text_from_monitors(text_to_find):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    with mss.mss() as sct:
        img = sct.grab(sct.monitors[0])
        img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(img_gray)
        return text_to_find in text

def get_text_with_color_filter(text_to_find, lower_bound, upper_bound):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    with mss.mss() as sct:
        img = sct.grab(sct.monitors[0])
        img_hsv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, lower_bound, upper_bound)
        res = cv2.bitwise_and(np.array(img), np.array(img), mask=mask)
        img_gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(img_gray)
        return text_to_find in text

def get_text_from_monitors2(text):
    return get_text_with_color_filter(text, np.array([40, 40, 40]), np.array([70, 255, 255]))

def get_text_from_monitors3(text):
    return get_text_with_color_filter(text, np.array([0, 100, 100]), np.array([10, 255, 255]))

def get_text_from_monitors4(text):
    return get_text_with_color_filter(text, np.array([100, 50, 50]), np.array([140, 255, 255]))

def start_script_with_email(email):
    global receiver_email_global, script_running
    if script_running:
        messagebox.showinfo("Script Running", "The script is already running.")
        return
    receiver_email_global = email
    script_running = True
    threading.Thread(target=main, daemon=True).start()

def gui_email_input():
    root = tk.Tk()
    root.title("Test Automation - Email Receiver")
    root.geometry("500x370")
    root.configure(bg="black")

    tk.Label(root, text="Enter Receiver Email:", fg="#00FF00", bg="black", font=("Arial", 12)).pack(pady=10)
    email_var = tk.StringVar()
    email_entry = tk.Entry(root, textvariable=email_var, width=40, bg="black", fg="#00FF00", insertbackground="#00FF00")
    email_entry.pack()

    label_result = tk.Label(root, text="Current Email: None", fg="#00FF00", bg="black", font=("Arial", 10))
    label_result.pack(pady=10)

    log_box = tk.Text(root, height=8, width=58, bg="black", fg="#00FF00", font=("Courier", 10))
    log_box.pack(pady=10)

    def write_to_log(msg):
        log_box.after(0, lambda: log_box.insert(tk.END, msg + "\n"))
        log_box.after(0, lambda: log_box.see(tk.END))

    global log_callback
    log_callback = write_to_log

    def on_start():
        email = email_var.get().strip()
        if "@" not in email:
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
            return
        label_result.config(text=f"Current Email: {email}")
        start_script_with_email(email)

    tk.Button(root, text="Start Script", command=on_start, bg="black", fg="#00FF00").pack(pady=10)
    root.mainloop()

def main():
    try:
        log("Main starting")
        absolute_path = os.path.dirname(__file__)
        full_image_path = os.path.join(absolute_path, "icons")

        sender_email = "tnvidia889@gmail.com"
        password = "dehqqeqffgwabqmw"
        receiver_email = receiver_email_global or "mareanagene8@gmail.com"

        Operation_StateMachine = 1

        while True:
            if Operation_StateMachine == 0:
                log("Searching for test started")
                if get_text_from_monitors("Next"):
                    Operation_StateMachine = 1

            elif Operation_StateMachine == 1:
                log("Searching for Pass/Fail")
                if get_text_from_monitors2("Test Result: Pass") or get_text_from_monitors2("Test Result; Pass"):
                    subject = "Test Pass"
                    body = "Hye, your test is over ."
                elif get_text_from_monitors3("Test Result: Fail") or get_text_from_monitors3("Test Result; Fail"):
                    subject = "Test Fail"
                    body = "Hye, your test is over ."
                else:
                    continue

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    message = MIMEMultipart()
                    message["From"] = sender_email
                    message["To"] = receiver_email
                    message["Subject"] = subject
                    message.attach(MIMEText(body, "plain"))
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                    log("Email sent successfully!")
                    Operation_StateMachine = 2

            elif Operation_StateMachine == 2:
                log("Waiting for a new test to start")
                if get_text_from_monitors("Test in progress"):
                    Operation_StateMachine = 1

    except KeyboardInterrupt:
        log("User keyboard interrupt")
    except Exception as error:
        log(f"Error: {error}")

if __name__ == "__main__":
    gui_email_input()
