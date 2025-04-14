import cv2
import numpy as np
import os

dataset_path = 'dataset'
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

faces = []
labels = []

dataset_path = 'dataset'

# Create the dataset directory if it doesn't exist
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

for filename in os.listdir(dataset_path):
    if filename.endswith('.jpg'):
        path = os.path.join(dataset_path, filename)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        label = int(filename.split('_')[0])  # Extract ID from filename like 123_0.jpg
        faces.append(img)
        labels.append(label)

if faces and labels:
    recognizer.train(faces, np.array(labels))
    recognizer.save('trained_model.yml')
    print("✅ Model trained and saved successfully.")
else:
    print("⚠️ No training data found in the dataset folder.")
