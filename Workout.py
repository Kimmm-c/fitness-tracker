from abc import ABC, abstractmethod
import numpy as np
import mediapipe as mp

class Workout(ABC):
    def __init__(self, name):
        self.name = name
        self.mp_pose = mp.solutions.pose

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    @abstractmethod
    def get_angle(self, landmarks):
        pass

    @abstractmethod
    def update_stage(self, angle, current_stage):
        pass


class BicepCurl(Workout):
    def __init__(self):
        super().__init__("Bicep Curls")

    def get_angle(self, landmarks):
        shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        return self.calculate_angle(shoulder, elbow, wrist)

    def update_stage(self, angle, current_stage):
        if angle > 160:
            return "down"
        elif angle < 30 and current_stage == "down":
            return "up"
        else:
            return current_stage


class LateralRaise(Workout):
    def __init__(self):
        super().__init__("Lateral Raise")

    def get_angle(self, landmarks):
        shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
               landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]

        return self.calculate_angle(elbow, shoulder, hip)

    def update_stage(self, angle, current_stage):
        if angle < 30:
            return "down"
        elif angle > 60 and current_stage == "down":
            return "up"
        else:
            return current_stage