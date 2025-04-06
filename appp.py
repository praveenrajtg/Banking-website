import cv2
import numpy as np
import os
import time
import json
import streamlit as st
import webbrowser
from PIL import Image

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
dataset_path = "face_dataset"

# Ensure dataset directory exists
os.makedirs(dataset_path, exist_ok=True)

def capture_face(username):
    cap = cv2.VideoCapture(0)
    safe_username = username.replace(" ", "_")
    user_folder = os.path.join(dataset_path, safe_username)
    os.makedirs(user_folder, exist_ok=True)
    count = 0
    
    while count < 50:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to access camera.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            cv2.imwrite(f"{user_folder}/{count}.jpg", face_roi)
            count += 1
    
    cap.release()
    return count

def train_recognizer():
    faces_data, labels = [], []
    username_mapping, current_label = {}, 0
    
    for username in os.listdir(dataset_path):
        user_folder = os.path.join(dataset_path, username)
        if os.path.isdir(user_folder):
            username_mapping[str(current_label)] = username
            for img_name in os.listdir(user_folder):
                if img_name.endswith('.jpg'):
                    img_path = os.path.join(user_folder, img_name)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    faces_data.append(img)
                    labels.append(current_label)
            current_label += 1
    
    if faces_data:
        recognizer.train(faces_data, np.array(labels))
        recognizer.save('face_recognizer.yml')
        with open('username_mapping.json', 'w') as f:
            json.dump(username_mapping, f)
        return True
    return False

def recognize_face(expected_username):
    if not os.path.exists('face_recognizer.yml'):
        return None, False
    
    try:
        with open('username_mapping.json', 'r') as f:
            username_mapping = json.load(f)
    except:
        return None, False
    
    recognizer.read('face_recognizer.yml')
    cap = cv2.VideoCapture(0)
    login_successful, recognized_username = False, None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            label, confidence = recognizer.predict(face_roi)
            
            if confidence < 70:
                recognized_username = username_mapping.get(str(label))
                
                if recognized_username == expected_username.replace(" ", "_"):
                    login_successful = True
                    break
                else:
                    st.error("Face does not match the entered name. Please try again!")
                    time.sleep(2)
            else:
                st.error("Face not recognized. Please try again!")
                time.sleep(2)
        
        if login_successful:
            break
    
    cap.release()
    return recognized_username, login_successful

st.title("NPR Bank Face Recognition")
option = st.sidebar.selectbox("Choose an option", ["Register", "Train Model", "Login"])

if option == "Register":
    username = st.text_input("Enter your full name:")
    if st.button("Capture Face") and username:
        count = capture_face(username)
        if count >= 50:
            st.success(f"Face data collected for {username}")
        else:
            st.error("Failed to capture sufficient face data.")

elif option == "Train Model":
    if st.button("Train Face Recognizer"):
        if train_recognizer():
            st.success("Face recognizer trained successfully!")
        else:
            st.error("No face data found. Please register a user first.")

elif option == "Login":
    username = st.text_input("Enter your registered name:")
    if st.button("Recognize Face") and username:
        safe_username = username.replace(" ", "_")
        
        # Check if the username is registered
        if not os.path.exists(os.path.join(dataset_path, safe_username)):
            st.error("You are not a registered customer. Please register first.")
        else:
            recognized_username, success = recognize_face(username)
            if success:
                st.success(f"Welcome, {username}!")

                # Save recognized username to a file
                with open("recognized_user.json", "w") as f:
                    json.dump({"username": username}, f)

                # Redirect to the HTML dashboard
                webbrowser.open("login_redirect.html")
            else:
                st.error("Face not recognized. Please try again.")
