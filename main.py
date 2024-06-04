from freenect2 import Device, FrameType
import numpy as np
import cv2

device = Device()
frames = {}
with device.running():
    for type_, frame in device:
        frames[type_] = frame
        if FrameType.Color in frames:
            color_frame = frames[FrameType.Color]
            color_image = color_frame.to_array()
            cv2.imshow('test', color_image)
            cv2.waitKey(1)
cv2.destroyAllWindows()
