# TinyGame by Kinect

## Description

通过Kinect V2实现体感游戏，目前已实现贪吃蛇。仅仅为抽象课程设计作业，缝合抽象但没有毛病。

设计理念：通过多线程实现freenect2更新全局变量color_image，cvzone.HandTrackingModule实现手掌识别推理，并实时更新相应游戏坐标信息。

## Requirements

### Hardware requirements

- Kinect V2 Xbox

- USB 3.0 controller. USB 2 is not supported.

### Operating system requirements

- Linux. (suggest Ubuntu 22.04LTS)

### Software requirements

- python >= 3.10. If lower than 3.9, there may be something wrong

- libfreenect2(https://github.com/OpenKinect/libfreenect2).

- opencv

- cvzone

- ...

tips: you better not use anaconda.

## Installation

```shell
git clone https://github.com/LuBoqi/RD.git
cd RD
pip3 install -r requirements.txt	#you need to do it by yourself, haha
```

## Table of files
.  
├── apple.png &emsp; #greedy snake  
├── dump_pcd.py &emsp; #use to test kinect v2 driver  
├── fruit.py &emsp; #cut fruit game  
├── head.png &emsp; #greedy snake  
├── images &emsp; #belongs to fruitGame  
├── libfreenect2 &emsp; #driver for kinect v2  
├── main.py &emsp; #test two things  
├── media_pipe.py &emsp; #identify hands  
├── output_big.pcd &emsp; #test file  
├── output.pcd &emsp; #test file  
├── README.md &emsp; #write by shabi  
├── ros_ws &emsp; #ros2 will be used in future   
├── SimHei.ttf &emsp; #used by greedy snake  
├── snakegame.py &emsp; #game code  
├── sound &emsp; #belongs to fruitGame  
└── temp_main.py &emsp; #rubbish  
## Thanks

- Ourselves
- OpenKinect(https://github.com/OpenKinect).
- Internet
- ChatGPT