from freenect2 import Device, FrameType
import numpy as np
import cv2
import _thread
import time
import mediapipe as mp
import math
import random
import cvzone
from cvzone.HandTrackingModule import HandDetector
from PIL import Image, ImageDraw, ImageFont


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
device = Device()
frames = {}
color_image = []


def cap_mat():
    global color_image
    with device.running():
        for type_, frame in device:
            frames[type_] = frame
            if FrameType.Color in frames:
                color_frame = frames[FrameType.Color]
                color_image = color_frame.to_array()


if __name__ == '__main__':
    _thread.start_new_thread(cap_mat, ())
    time.sleep(1)
    with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while True:
            image = color_image
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                              mp_drawing_styles.get_default_hand_landmarks_style(),
                                              mp_drawing_styles.get_default_hand_connections_style())
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            cv2.waitKey(1)

cap = cv2.VideoCapture(0)  # 0为自己的摄像头
cap.set(3, 1280)  # 宽
cap.set(4, 720)  # 高

detector = HandDetector(detectionCon=0.8, maxHands=1)

startGame = False


# 计算向量积
def cross(pt1, pt2, pt3):
    return (pt2[0] - pt1[0]) * (pt3[1] - pt1[1]) - (pt2[1] - pt1[1]) * (pt3[0] - pt1[0])


# 解决cv2.putText绘制中文乱码
def cv2AddChineseText(image, text, position, textColor=(255, 255, 255), textSize=50):
    if isinstance(image, np.ndarray):  # 判断是否OpenCV图片类型
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(image)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "wqy-zenhei.ttc", textSize, encoding="utf-8") #使用系统中存在的中文字体
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)


class SnakeGameClass:
    def __init__(self, pathFood, pathHead):  # 构造方法
        self.points = []  # 蛇身上所有的点
        self.lengths = []  # 每个点之间的长度
        self.currentLength = 0  # 蛇的总长
        self.allowedLength = 150  # 蛇允许的总长度
        self.previousHead = 0, 0  # 第二个头结点

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.imgHead = cv2.imread(pathHead, cv2.IMREAD_UNCHANGED)
        self.hHead, self.wHead, _ = self.imgHead.shape
        self.angle = 0

        self.score = 0
        self.gameOver = False
        self.gameoverFlag = False

        self.handIndex = 0

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead, Hands):  # 实例方法

        if self.gameOver:
            imgMain = cv2AddChineseText(imgMain, "游戏结束", [450, 200], textColor=(255, 0, 0), textSize=80)
            imgMain = cv2AddChineseText(imgMain, f'你的分数:{self.score}', [450, 350], textColor=(255, 0, 0),
                                        textSize=80)
            self.gameoverFlag = True

        else:
            px, py = self.previousHead
            cx, cy = currentHead

            if cv2.norm(self.previousHead, currentHead, cv2.NORM_L2) > 5:
                self.points.append([cx, cy])  # 添加蛇的点列表节点
                distance = math.hypot(cx - px, cy - py)  # 两点之间的距离
                self.lengths.append(distance)  # 添加蛇的距离列表内容
                self.currentLength += distance
                self.previousHead = cx, cy

            # 收缩长度
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # 判断是否吃了食物
            rx, ry = self.foodPoint

            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1

            # 画蛇
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        self.points[i - 1] = tuple(self.points[i - 1])  # 转换数据格式22
                        self.points[i] = tuple(self.points[i])  # 转换数据格式22
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 30)
                # 画蛇头
                if len(self.points) >= 2:
                    x1, y1 = self.points[-2]  # 倒数第二个点的坐标
                    x2, y2 = self.points[-1]  # 最后一个点的坐标

                    delta_x = x2 - x1
                    delta_y = y2 - y1

                    # 计算角度
                    self.angle = -np.arctan2(delta_y, delta_x) * 180 / np.pi + 90

                    # 获得旋转变换矩阵
                    rotation_matrix = cv2.getRotationMatrix2D((self.wHead // 2, self.hHead // 2), self.angle, 1.0)

                    # 应用旋转变换矩阵进行图像旋转
                    rotated_image = cv2.warpAffine(self.imgHead, rotation_matrix, (self.wHead, self.hHead))

                    imgMain = cvzone.overlayPNG(imgMain, rotated_image, (
                        self.points[-1][0] - self.wHead // 2, self.points[-1][1] - self.hHead // 2))

                self.points[-1] = tuple(self.points[-1])  # 转换数据格式22

            # 画食物
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))
            imgMain = cv2AddChineseText(imgMain, f'分数:{self.score}', [40, 30], textColor=(255, 255, 255), textSize=35)

            if len(self.points) >= 4:
                for i, point in enumerate(self.points):
                    if i < len(self.points) - 3:
                        if i > 0 > cross([cx, cy], [px, py], self.points[i]) * cross([cx, cy], [px, py],
                                                                                     self.points[i + 1]) and cross(
                            self.points[i], self.points[i + 1], [cx, cy]) * cross(
                            self.points[i], self.points[i + 1], [px, py]) < 0:
                            self.gameOver = True
                            self.points = []  # 蛇身上所有的点
                            self.lengths = []  # 每个点之间的长度
                            self.currentLength = 0  # 蛇的总长
                            self.allowedLength = 150  # 蛇允许的总长度
                            self.previousHead = 0, 0  # 第二个头结点
                            self.randomFoodLocation()
        return imgMain


game = SnakeGameClass("apple.png", "head.png")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # 将手水平翻转
    imgOutput = img.copy()
    hands, img = detector.findHands(img, flipType=False)  # 左手是左手，右手是右手，映射正确

    if startGame:
        if hands:
            lmList = hands[0]['lmList']  # hands是由N个字典组成的列表
            pointIndex = lmList[8][0:2]  # 只要食指指尖的x和y坐标
            pointIndex = tuple(pointIndex)  # 转换数据格式22
            hand = hands[0]

            img = game.update(img, pointIndex, hand)
        else:
            if game.gameOver:
                img = cv2AddChineseText(img, '手势贪吃蛇', [400, 200], textColor=(255, 0, 0), textSize=100)
                img = cv2AddChineseText(img, '按s开始游戏', [550, 380], textColor=(255, 0, 0), textSize=40)
                startGame = False

    else:
        img = cv2AddChineseText(img, '手势贪吃蛇', [400, 200], textColor=(255, 0, 0), textSize=100)
        img = cv2AddChineseText(img, '按s开始游戏', [550, 380], textColor=(255, 0, 0), textSize=40)

    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WND_PROP_FULLSCREEN)
    cv2.imshow("Image", img)

    key = cv2.waitKey(1)

    if key == ord('s'): # 按s键开始游戏
        startGame = True
        game.gameOver = False
        game.score = 0
