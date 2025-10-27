import cv2
import mediapipe as mp
import numpy as np
import json
import socket

def Pose_Images():
    # --- UDP Setup ---
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest_addr = ('127.0.0.1', 5052)
    print(f"Streaming pose data to {dest_addr} via UDP...")

    # --- MediaPipe Pose Setup ---
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.8) as pose:
        
        # --- Camera Setup ---
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # --- Pose Estimation ---
            results = pose.process(image)

            # --- Draw Pose and Send Data ---
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            pose_data = []
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS)
                
                # Package landmark data into a list of dictionaries
                for landmark in results.pose_landmarks.landmark:
                    pose_data.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })

                # --- Send Data via UDP ---
                try:
                    json_data = json.dumps(pose_data)
                    text_to_send = json_data.encode('utf-8')
                    udp_socket.sendto(text_to_send, dest_addr)
                except Exception as e:
                    print(f"Error sending UDP data: {e}")
            
            # Display the image
            cv2.imshow('MediaPipe Pose', image)

            # Exit on 'q' key
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        udp_socket.close()

if __name__ == '__main__':
    Pose_Images()