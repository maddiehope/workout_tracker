# Mediapipe & M5Stick Workout Tracker
This project is a repetition counting program that uses the Mediapipe Pose module to track the number of repetitions of a particular exercise, and was a solution for an assignment in ELEE 2045. The user initiates the repetition counting by hitting the M5StickCPlus smartwatch's main button. The program uses BLE to communicate with the smartwatch. A complete repetition is defined by the user by hitting the M5StickCPlus main button. During the workout, the program uses computer vision (cv2 library) to track what is happening via the webcam and to display the repetition count, repetitions per second, and the user's pose targets. The program uses a three-state machine to count repetitions. At any point, the user can hit the button on the M5StickCPlus again to finish the workout, which is indicated on the screen.

<b> Video Demonstration: https://youtu.be/cLX6_wTYfWg </b>


## Accomplishments/Failures
I was pretty successful in this lab, and am proud of the results. I am glad we were able to experiment with the media pipe library because there are many possibilities for its use in the future. It is also interesting to see some machine learning aspects we are talking about in INFO 3000 be implemented. 

## Reflections

The main difference between my work and the solutions is that I didn't configure lines that mark the top & bottom y positions. This would've been helpful for the user to see where exactly they need to hit for a rep to be counted. I could have added this easily by inserting "cv2.line(frame, ...)" into my code. 

An addition I could've added to part 1 that would have improved my program is a unique text statement when the user first quits the rep counting & is waiting to start again. The solution uses the sentence "Hit the button to start again" to accomplish this. I tried adding something similar but couldn't figure out the logic to display it correctly without an overlay of "hit to start again" and "hit to start" messages. I only spent a little time problem-solving this because I didn't think it was essential, but it is just a detail that could be added later.
