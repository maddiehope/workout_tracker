''' 
Part 1: Repetition Counting
Pose module documentation: https://google.github.io/mediapipe/solutions/pose.html

In this example, they suggest that this library can be used to track the number of repetitions of a particular exercise. 
Your goal is to actually do this (in a limited fashion).
The “user” is the person exercising. 
Let's assume they are also wearing a smart watch (the M5StickCPlus), which will be used to initiate the repetition counting. 
You can use Bluetooth or MQTT to communicate.

A complete repetition is defined by the user by hitting the M5StickCPlus main button. 
The first time, the user should be standing up straight. 
The second time, they should be squatting down at their target height.
Once the user hits the button the second time, the workout begins. You can count repetitions by using the following three-state machine:

• Start -> Top when the user is in state Start and their head gets near or above a target y value.
• Top -> Bottom when the user is in state Top and their head gets near or below a target y value.
• Bottom -> Top when the user is in state Bottom and their head gets near or above a target y value. This event also triggers a repetition count.

During the workout, you should display the repetition count, repetitions per second, and display their pose targets. 
At any point, they should be able to hit the button on the M5StickCPlus again to finish the workout, which should be indicated on screen.
'''
# -------------------------------------------------------------------------------------------
import asyncio
from bleak import BleakScanner
from bleak import BleakClient
import struct
import time

import cv2 
import numpy as np
import mediapipe as mp

import threading

connected = False

# INITIALIZING VARIABLES 
top = 0.0  
bottom = 0.0  
press_count = 0  
button_press = (0,)  
prev_button_press = (0,)  
state = "Start"  
rep_count = 0  
start_time = None  
elapsed_time = 0

# POSE DETECTION INSERTION ----------------------

mp_pose = mp.solutions.pose
pose_detection = mp_pose.Pose(static_image_mode=False, # uses previous image as context
                              min_tracking_confidence = 0.5, # more accurate positioning 
                              min_detection_confidence= 0.5) # raise to have less false detections

# FUNCTIONS -------------------------------------

# STATE MACHINE
def press_tracker(button_press):
    '''
    Function to control the value of press_count so the state machinr can function accordingly.
    INPUT: button_press (message that was sent as a notification from arduino)
    -> press_count == 1 : machine started, top value will be attained
    -> press_count == 2 : repitions begin to be counted, bottom value attained
    -> press_count == 3 : workout/repition count ended
    '''
    global press_count
    global prev_button_press
    global state
    global rep_count
    global start_time
    global head_y
    global elapsed_time
    #global connected ##

    if button_press == (1,) and prev_button_press == (0,):
        press_count += 1
        #print("Button press is:", button_press) ##

        if press_count == 1:
            print("1")
            state = "Top"
            start_time = cv2.getTickCount()

        elif press_count == 2:
            print("2, repetitions starting.")
            state = "Bottom"

        elif press_count == 3:
            print("3, workout ending.")

            # re-setting all variables
            press_count = 0
            rep_count = 0
            button_press = (0,)
            state ="Start"
            start_time = None
            elapsed_time = 0
            #connected = False ##

    prev_button_press = button_press

# CONNECTING DEVICE THROUGH BLE
async def run():
    global state

    print("Searching devices...")
    state = "Connecting"
    devices = await BleakScanner.discover()

    def notification_callback(sender, payload):
        print(sender, payload)

    # Bleak connection aided by https://github.com/naoki-sawada/m5stack-ble/blob/master/client/main.py
    device = list(filter(lambda d: d.name == "M5StickCPlus-Maddie", devices))

    if len(device) == 0:
        print("Device 'M5StickCPlus-Maddie' NOT found.")
    else:
        print("Device 'M5StickCPlus-Maddie' found.")

        address = device[0].address
        global connected
        global button_press # (1,): press & (0,): released

        async with BleakClient(address) as client:
            print("Connecting to device...")
            connected = True

            print("Connected.")
            state = "Start"

            while connected:
              button_data_bytes = await client.read_gatt_char("e672f43d-ee01-4e48-bf96-4e772413c930")
              button_press = struct.unpack('<b', button_data_bytes[:1])
              press_tracker(button_press) ##
              ## print("Called press_tracker.")
              await asyncio.sleep(0.5)

def run_controller():
    asyncio.run(run())

# starting threading for run_controller()
t = threading.Thread(target=run_controller) # in theory, multiple m5 sticks would work
t.start() 

# MAIN LOOP 
def main():
    global frame
    global connected

    cap = cv2.VideoCapture(0) # 0 is an index to the first camera

    while cap.isOpened():
        res, frame = cap.read() # ret will indicate success or failure, frame is a numpy array

        if not res:
            continue # no frame read

        process_frame(frame)

        cv2.imshow("Workout", frame) # quick gui

        if cv2.waitKey(1) == ord('q'):
            connected = False
            break

    cap.release() # stop the camera
    cv2.destroyAllWindows() # closes the open gui window

    t.join()  # wait for run_controller thread to finish 


# PROCESSING THE FRAME
def process_frame(frame):
  global state
  global rep_count
  global start_time
  global press_count
  global button_press
  global prev_button_press
  global elapsed_time
  global top
  global bottom


  pose_detection_results = pose_detection.process(frame) # find any poses
  
  if pose_detection_results.pose_landmarks:

    '''
    print(
          f'Nose coordinates: ('
          f'{pose_detection_results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x }, '
          f'{pose_detection_results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y })'
         )
    '''

    head_y = pose_detection_results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y
    # print(head_y) ##

    if state == "Start":
      cv2.putText(frame, "Stand straight up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
      cv2.putText(frame, "Press the button to start", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    elif state == "Connecting":
      cv2.putText(frame, "Awaiting connection", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    else: 
      if state == "Top": # initial top state- getting standing y val
        top = head_y
        cv2.putText(frame, "Squat down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, "Press the button to start counting", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

      elif state == "Top Rep" and head_y >= top: # repititve top state
        state = "Bottom Rep"

      elif state == "Bottom": # initial bottom state- getting squatting y val
        rep_count += 1
        bottom = head_y
        state = "Top Rep"

        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()

      elif state == "Bottom Rep" and head_y <= bottom: # repetitive bottom state
        rep_count += 1
        state = "Top Rep"

        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        
      if elapsed_time != 0: # doing this so text is not overlayed for inital top
        #print(f"Repetition count: {rep_count}, Repetitions per second: {rep_count / elapsed_time:.2f}") ##
        cv2.putText(frame, f"Rep count: {rep_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f"Reps per sec: {rep_count / elapsed_time:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

  else:
    print("Empty camera frame.")
    cv2.putText(frame, "Please move back in frame", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

  return frame 
           
# -----------------------------------------------

if __name__=="__main__":
    main()

# -------------------------------------------------------------------------------------------            

