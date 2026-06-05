import cv2


class CameraService:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)

    def is_opened(self):
        return self.cap.isOpened()

    def read(self):
        success, frame = self.cap.read()
        if not success:
            return False, None
        return True, cv2.flip(frame, 1)

    def release(self):
        self.cap.release()

