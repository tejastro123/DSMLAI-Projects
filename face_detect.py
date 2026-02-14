import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

# Load OpenCV's Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the camera
cap = cv2.VideoCapture(0)

# Create Tkinter window
root = tk.Tk()
root.title("Face Detection App")

# Video display label
label = Label(root)
label.pack()

def detect_faces():
    ret, frame = cap.read()
    if not ret:
        return
    
    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Convert the frame to an image for Tkinter
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    
    label.imgtk = imgtk
    label.configure(image=imgtk)
    
    # Repeat after 10ms
    label.after(10, detect_faces)

def close_app():
    cap.release()
    root.destroy()

# Start button
start_btn = Button(root, text="Start Detection", command=detect_faces, font=("Arial", 12))
start_btn.pack(pady=10)

# Exit button
exit_btn = Button(root, text="Exit", command=close_app, font=("Arial", 12))
exit_btn.pack(pady=10)

root.mainloop()
