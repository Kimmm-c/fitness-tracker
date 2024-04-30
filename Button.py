import cv2


class Button:
    def __init__(self, mode, top_left, bot_right, color):
        self.mode = mode
        self.top_left = top_left
        self.bot_right = bot_right
        self.text = mode.name
        self.color = color
        self.btn_text_baseline = 40
        self.padding = 10

    def draw(self, img):
        cv2.rectangle(img, self.top_left, self.bot_right, self.color, -1)
        cv2.putText(img, self.text, (self.top_left[0] + self.padding, self.top_left[1] + self.btn_text_baseline),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)