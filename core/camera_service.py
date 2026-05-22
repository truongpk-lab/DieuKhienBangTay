import cv2


class CameraService:
    def __init__(self, camera_index=0):
        self.capture = cv2.VideoCapture(camera_index)

    def is_opened(self):
        return self.capture.isOpened()

    def read(self):
        return self.capture.read()

    def release(self):
        self.capture.release()
