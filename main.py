import _thread
import math
import random
import time
import cvzone
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from freenect2 import Device, FrameType

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
device = Device()
frames = {}
color_image = []
startGame = False


def cap_mat():
    global color_image
    with device.running():
        for type_, frame in device:
            frames[type_] = frame
            if FrameType.Color in frames:
                color_frame = frames[FrameType.Color]
                color_image = color_frame.to_array()


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
    font_path = os.path.join(os.path.dirname(__file__), "SimHei.ttf")
    fontStyle = ImageFont.truetype(font_path, textSize, encoding="utf-8")
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

    def update(self, imgMain, currentHead):  # 实例方法
        global startGame
        if self.gameOver:
            startGame = False
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


# 判断是否握拳的函数
def is_fist(landmarks):
    # 提取手指尖和指根的关键点
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # 检查手指尖是否都在指根附近（靠近手掌）
    if (thumb_tip.y > thumb_ip.y and
            index_tip.y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
            middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
            ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_MCP].y and
            pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_MCP].y):
        return True
    return False


if __name__ == '__main__':
    _thread.start_new_thread(cap_mat, ())
    time.sleep(1)
    game = SnakeGameClass("apple.png", "head.png")
    with mp_hands.Hands(model_complexity=0, max_num_hands=1, min_detection_confidence=0.8,
                        min_tracking_confidence=0.1) as hands:
        while True:
            img = color_image
            img.flags.writeable = False
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img)
            # Draw the hand annotations on the img.
            img.flags.writeable = True
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                              mp_drawing_styles.get_default_hand_landmarks_style(),
                                              mp_drawing_styles.get_default_hand_connections_style())
                    if is_fist(hand_landmarks.landmark):
                        startGame = True
                        game.gameOver = False
                        game.score = 0
                    x, y = hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y
                    x, y = x * img.shape[1], y * img.shape[0]
                    x, y = int(x), int(y)
            if startGame:
                if results:
                    pointIndex = (x, y)
                    img = game.update(img, pointIndex)
            elif game.gameOver:
                    img = cv2AddChineseText(img, '手势贪吃蛇', [400, 200], textColor=(255, 0, 0), textSize=100)
                    img = cv2AddChineseText(img, '握拳或按s开始游戏', [550, 380], textColor=(255, 0, 0),
                                            textSize=40)
                    img = cv2AddChineseText(img, f'上局的分数:{game.score}', [450, 850],
                                            textColor=(255, 0, 0), textSize=80)
                    startGame = False

            else:
                print('else')
                img = cv2AddChineseText(img, '手势贪吃蛇', [400, 200], textColor=(255, 0, 0), textSize=100)
                img = cv2AddChineseText(img, '握拳或按s开始游戏', [550, 380], textColor=(255, 0, 0), textSize=40)

                startGame = False

            cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WND_PROP_FULLSCREEN)
            cv2.imshow("Image", img)

            key = cv2.waitKey(1)

            if key == ord('s'):  # 按s键开始游戏
                startGame = True
                game.gameOver = False
                game.score = 0
            elif key == ord('q'):
                startGame = False
                game.gameOver = False
                game.score = 0
