import cv2
import mediapipe as mp
import numpy as np
from Workout import BicepCurl, LateralRaise
from Button import Button


class FitnessTracker:
    def __init__(self, *args):
        self.name = "Fitness Tracker"
        self.cap = cv2.VideoCapture(0)
        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))
        self.counter = 0
        self.stage = None
        self.btn_height = 73
        self.btn_width = 200
        self.margin = 20
        self.modes = list(args)
        self.mode_count = len(self.modes)
        self.current_workout = self.modes[0]
        self.buttons = []
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        try:
            self.create_buttons()
        except Exception as e:
            print(e)

    def create_buttons(self):
        for i in range(self.mode_count):
            if len(self.buttons) == 0:
                self.buttons.append(Button(self.modes[i],
                                           (0, self.btn_height + self.margin),
                                           (self.btn_width, self.btn_height + self.margin + self.btn_height),
                                           (255, 0, 0)))
            else:
                # Check if button is out of bounds
                if self.buttons[-1].bot_right[1] + self.margin + self.btn_height <= self.frame_height:
                    self.buttons.append(Button(self.modes[i],
                                               (0, self.buttons[-1].bot_right[1] + self.margin),
                                               (self.btn_width,
                                                self.buttons[i - 1].bot_right[1] + self.margin + self.btn_height),
                                               (255, 0, 0)))
                else:
                    raise Exception("Button out of bounds")

    def run(self):
        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self.on_mouse_click)

        while self.cap.isOpened():
            ret, frame = self.cap.read()

            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make detection
            results = self.pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                self.update_workout(landmarks, image)
            except:
                pass

            self.update_graphics(image, results)

            cv2.imshow(self.name, image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def update_workout(self, lm, img):
        # Update workout stage
        angle = self.current_workout.get_angle(lm)
        current_stage = self.stage
        self.stage = self.current_workout.update_stage(angle, self.stage)

        # Update rep count
        if current_stage == "down" and self.stage == "up":
            self.counter += 1

        # Render current angle
        elbow = [lm[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 lm[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

        cv2.putText(img, str(angle),
                    tuple(np.multiply(elbow, [640, 480]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                    )

    def update_graphics(self, img, res):
        # Update rep count
        cv2.rectangle(img, (0, 0), (250, self.btn_height), (245, 117, 16), -1)
        cv2.putText(img, 'REPS', (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img, str(self.counter),
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Update stage
        cv2.putText(img, 'STAGE', (65, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img, self.stage,
                    (60, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Update current workout
        cv2.putText(img, 'Current Workout: ' + self.current_workout.name, (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Render buttons
        for btn in self.buttons:
            btn.draw(img)

        # Render detections
        self.mp_drawing.draw_landmarks(img, res.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                       self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                       )

    def switch_workout(self, new_workout):
        print(f"Switching workout to {new_workout.name}")
        self.current_workout = new_workout
        self.counter = 0
        self.stage = None

    def on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Mouse clicked at {x}, {y}")
            for btn in self.buttons:
                if btn.top_left[0] < x < btn.bot_right[0] and btn.top_left[1] < y < btn.bot_right[1]:
                    self.switch_workout(btn.mode)
                    break


if __name__ == "__main__":
    bicep_curls = BicepCurl()
    lateral_raises = LateralRaise()
    app = FitnessTracker(bicep_curls, lateral_raises)
    app.run()
