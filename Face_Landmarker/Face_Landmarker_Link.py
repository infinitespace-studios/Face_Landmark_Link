import mediapipe as mp
import numpy as np
import cv2
import csv

from mediapipe.python.solutions import face_mesh
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

# import matplotlib
# import matplotlib.pyplot as plt

# from timecode import Timecode

import tkinter as tk
from tkinter import filedialog

import os

# madiea pipe face landmarker options
model_path = "face_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a face landmarker instance with the video mode:
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    output_face_blendshapes=True)


### DEFINE DRAW LANDMARKS
def draw_landmarks_on_image(rgb_image, detection_result):
    face_landmarks_list = detection_result.face_landmarks
    annotated_image = np.copy(rgb_image)

    # Loop through the detected faces to visualize.
    for idx in range(len(face_landmarks_list)):
        face_landmarks = face_landmarks_list[idx]

        # Draw the face landmarks.
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        face_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
        ])

        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_tesselation_style())
        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_contours_style())
        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_iris_connections_style())

    return annotated_image

####### Use OpenCV’s VideoCapture to load the input video.


# here i make an open file dialogue window
# Create a Tkinter root window
root = tk.Tk()
root.withdraw()  # Hide the root window

# Open the file dialog to select the video file
file_path = filedialog.askopenfilename(title="Select Video File")

# Check if the user selected a file
if file_path:
    # Continue with the rest of your code using the file_path variable
    # ...
    video_path = file_path
else:
    print("No file selected.")
    


# Load the frame rate of the video using OpenCV’s CV_CAP_PROP_FPS
# You’ll need it to calculate the timestamp for each frame.

# Path to the input video file
#video_path = "???.mp4"

# Path to the output CSV file
file_name = os.path.basename(file_path)
# print (file_name)
file_result, extension = os.path.splitext(file_name)
# print(file_result)
output_csv_path = str(file_result) + "_blendshape_data.csv"
# print (output_csv_path)

# Create a VideoCapture object
cap = cv2.VideoCapture(video_path)

# Check if the video file was successfully opened
if not cap.isOpened():
    print("Error opening video file")
    exit()

# Get the frame rate of the video
frame_rate = cap.get(cv2.CAP_PROP_FPS)
# frame_rate = 60

# Calculate the timestamp for each frame
frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
total_time = frame_count / frame_rate

# print("Frame rate:", frame_rate)
# print("Total time:", total_time, "seconds")

# List of blendshape names
blendshape_names = [
    "EyeBlinkLeft", "EyeLookDownLeft", "EyeLookInLeft", "EyeLookOutLeft", "EyeLookUpLeft",
    "EyeSquintLeft", "EyeWideLeft", "EyeBlinkRight", "EyeLookDownRight", "EyeLookInRight",
    "EyeLookOutRight", "EyeLookUpRight", "EyeSquintRight", "EyeWideRight", "JawForward",
    "JawRight", "JawLeft", "JawOpen", "MouthClose", "MouthFunnel", "MouthPucker", "MouthRight",
    "MouthLeft", "MouthSmileLeft", "MouthSmileRight", "MouthFrownLeft", "MouthFrownRight",
    "MouthDimpleLeft", "MouthDimpleRight", "MouthStretchLeft", "MouthStretchRight",
    "MouthRollLower", "MouthRollUpper", "MouthShrugLower", "MouthShrugUpper", "MouthPressLeft",
    "MouthPressRight", "MouthLowerDownLeft", "MouthLowerDownRight", "MouthUpperUpLeft",
    "MouthUpperUpRight", "BrowDownLeft", "BrowDownRight", "BrowInnerUp", "BrowOuterUpLeft",
    "BrowOuterUpRight", "CheekPuff", "CheekSquintLeft", "CheekSquintRight", "NoseSneerLeft",
    "NoseSneerRight", "TongueOut", "HeadYaw", "HeadPitch", "HeadRoll", "LeftEyeYaw",
    "LeftEyePitch", "LeftEyeRoll", "RightEyeYaw", "RightEyePitch", "RightEyeRoll"
]
# Create a CSV file and write the header
header = ["Timecode", "BlendShapeCount"] + blendshape_names
with open(output_csv_path, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)
    
    # Loop through each frame
    while cap.isOpened():
        # Read the current frame
        ret, frame = cap.read()

        # Check if the frame was successfully read
        if not ret:
            break

        # Get the current frame index
        frame_index = cap.get(cv2.CAP_PROP_POS_FRAMES)

        # Calculate the timestamp for the current frame
        frame_timestamp_ms = int(frame_index * (1000 / frame_rate)) 
        milliseconds = int((frame_index) % frame_rate)   # 60 is the Live link default
        seconds = int((frame_timestamp_ms / 1000) % 60)
        minutes = int((frame_timestamp_ms / (1000 * 60)) % 60)
        hours = int(frame_timestamp_ms / (1000 * 60 * 60))

        frame_index_formatted = int(frame_index % 1000)

        time_formatted = f"{(hours):02d}:{minutes:02d}:{seconds:02d}:{milliseconds:02}.{frame_index_formatted:03d}"
        # print("Formatted Time:", time_formatted)

        # Convert the frame received from OpenCV to a MediaPipe’s Image object.
        frame_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_array)
           
        # Perform face landmarking on the provided single image.
        # The face landmarker must be created with the video mode.
        with FaceLandmarker.create_from_options(options) as landmarker:
            face_landmarker_result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
            # print(face_landmarker_result)

            face_blendshapes = face_landmarker_result.face_blendshapes[0]
            # Create a list to hold all blendshape scores
            all_blendshape_scores = []

            
            # Iterate through the face blendshapes starting from index 1 to skip the neutral shape
            for face_blendshapes_category in face_blendshapes[1:]:
                blendshape_name = face_blendshapes_category.category_name
                blendshape_score = face_blendshapes_category.score
                formatted_score = "{:.8f}".format(blendshape_score)
                # print(blendshape_name + ":" + formatted_score)

                # Process or store the blendshape name and score                

                # Add the formatted score to the list
                all_blendshape_scores.append(formatted_score)

                 
            #The order of the indexes in this list needs to be remade
            new_order = [8, 10, 12, 14, 16, 18, 20, 9, 11, 13, 15, 17, 19, 21, 22, 25, 23, 24, 26, 31, 37, 38, 32, 43, 44, 29, 30, 27, 28, 45, 46, 39, 40, 41, 42, 35, 36, 33, 34, 47, 48, 0, 1, 2, 3, 4, 5, 6, 7, 49, 50]
            all_blendshape_scores_sorted =[all_blendshape_scores[i] for i in new_order]
            # print("New one: " + str(all_blendshape_scores_sorted))

            num_blendshapes = len(face_blendshapes[1:])  # Exclude the first blendshape (neutral shape)
            # print("Number of found blendshapes:", num_blendshapes)    

            # Create a list of eight zeros
            additional_columns = [0] * 10
            
            blendshape_data = [time_formatted] +  [num_blendshapes] + all_blendshape_scores_sorted + additional_columns


        

        # Write the data row to the CSV file
        writer.writerow(blendshape_data)     

        # Display the frame drawing FaceMesh and timestamp
        annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), face_landmarker_result)        
        cv2.imshow("Frame", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    
        # Display the frame and timestamp
        # cv2.imshow("Frame", frame)
        # print("Frame:", frame_index, "Timestamp:", frame_timestamp_ms, "milliseconds")

        # Check if the 'q' key is pressed to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()

