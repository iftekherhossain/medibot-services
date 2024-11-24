import cv2
import mediapipe as mp
import pickle
import matplotlib.pyplot as plt
import numpy as np
import statistics

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
x_list = []
cap = cv2.VideoCapture("tremor.mp4")

def count_direction_changes(values, threshold):
    # Initialize variables
    direction_changes = 0
    current_direction = None  # Track current direction, either "up" or "down"

    # Loop through each pair of consecutive values
    for i in range(1, len(values)):
        # Calculate the difference between consecutive values
        diff = values[i] - values[i - 1]
        if abs(diff) >= threshold:
            # Determine the direction: "up" or "down"
            if diff > 0:
                new_direction = "up"
            elif diff < 0:
                new_direction = "down"
            else:
                new_direction = None  # No change if diff is 0

            # Count change in direction
            if current_direction and new_direction and current_direction != new_direction:
                direction_changes += 1

            # Update the current direction
            current_direction = new_direction

    return direction_changes
with mp_hands.Hands(model_complexity=0,max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      break

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    # print(results)
    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        x = float(f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y}')
        x_list.append(x)
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
  cap.release()
print(x_list)
Q1 = np.percentile(x_list, 45)
Q3 = np.percentile(x_list, 55)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

filtered_values = [x for x in x_list if lower_bound <= x <= upper_bound]
variance = statistics.variance(filtered_values)
std = statistics.stdev(filtered_values)
print(std)
count = count_direction_changes(filtered_values,0.005)
print("count",count)
if count> 10:
  print("Tremon")
else:
  print("Normal")