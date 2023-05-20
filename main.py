import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import math
import random
import pygame
from pygame import mixer, mixer_music

pygame.init()

#background
mixer.music.load('background.wav')
mixer.music.play(-1)

cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)

detector = HandDetector(detectionCon=0.8, maxHands=1)
class SnakeGame:
    def __init__(self,pathFood="apple.png",pathBomb="bomb1.png"):
        self.points = []
        self.lengths = []
        self.currLen = 0
        self.allowedLen = 150
        self.prvHead = 0,0
        self.score = 0
        self.finalScore = 0
        self.imgFood = cv2.imread(pathFood,cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood,_ = self.imgFood.shape
        self.imgBomb = cv2.imread(pathBomb,cv2.IMREAD_UNCHANGED)
        self.hBomb, self.wBomb,_ = self.imgBomb.shape
        self.foodPoint = 0,0
        self.bombPoint = 0,0
        self.randomFoodLoc()
        self.gameOver = False
    
    def randomFoodLoc(self):
        self.foodPoint = random.randint(0,1000),random.randint(0,600)
    def randomBombLoc(self):
        self.bombPoint = random.randint(0,1000),random.randint(0,600)

    def update(self,imgMain,currHead):
        if self.gameOver:
            cvzone.putTextRect(imgMain,"Game Over",[300,400],scale=7,thickness=5,font = cv2.FONT_HERSHEY_PLAIN)
            cvzone.putTextRect(imgMain,f'Score: {self.finalScore}',[300,550],scale=7,thickness=5,font = cv2.FONT_HERSHEY_PLAIN)
            self.score = 0
            
        else:
            px,py = self.prvHead
            cx,cy = currHead
            self.points.append([cx,cy])
            dist = math.hypot(cx-px,cy-py)
            self.lengths.append(dist)
            self.currLen += dist
            self.prvHead = currHead
            if self.currLen > self.allowedLen:
                for i, length in enumerate(self.lengths):
                    self.currLen -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currLen <= self.allowedLen:
                        break            
            rx, ry = self.foodPoint
            bx,by = self.bombPoint
            if rx - self.wFood//2 < cx < rx + self.wFood//2 and ry - self.hFood//2 < cy < ry + self.hFood//2:
                apple = mixer.Sound('applecrunch.wav')
                apple.play()
                self.randomBombLoc()
                self.randomFoodLoc()
                self.allowedLen += 60
                self.score += 1
            if bx - self.wBomb//2 < cx < bx + self.wBomb//2 and by - self.hBomb//2 < cy < by + self.hBomb//2:
                self.gameOver = True
                gmeOver = mixer.Sound('gameover.mp3')
                gmeOver.play()
                self.points = []
                self.lengths = []
                self.currLen = 0
                self.allowedLen = 150
                self.prvHead = 0,0
                self.finalScore = self.score
                cv2.putText(imgMain,"Game Over",(100,100),cv2.FONT_HERSHEY_PLAIN,5,(0,0,255),5)   
                # self.randomFoodLoc()
                # self.allowedLen += 60
                # self.score += 1
            if (self.points):
                for i,point in enumerate(self.  points):
                    if i !=0:
                        cv2.line(imgMain,self.points[i-1],self.points[i],(0,255,0),20)
                cv2.circle(imgMain, self.points[-1], 10, (255, 0, 255), cv2.FILLED)
            
            if len(self.points) > 2:
                pts = np.array(self.points[:-2],np.int32)
                pts.reshape((-1,1,2))
                cv2.polylines(imgMain,[pts],False,(0,0,255),5)
                minDist = cv2.pointPolygonTest(pts,currHead,True)
                if -0.9 <= minDist <= 0.9 :
                    self.gameOver = True
                    gmeOver = mixer.Sound('gameover.mp3')
                    gmeOver.play()
                    self.points = []
                    self.lengths = []
                    self.currLen = 0
                    self.allowedLen = 150
                    self.prvHead = 0,0
                    self.finalScore = self.score
                    cv2.putText(imgMain,"Game Over",(100,100),cv2.FONT_HERSHEY_PLAIN,5,(0,0,255),5)    
            rx,ry = self.foodPoint
            bx,by = self.bombPoint
            while not (rx - (self.wFood//2) > 0 and ry - (self.hFood//2) > 0):
                self.randomFoodLoc()
                rx,ry = self.foodPoint
            while not (bx - (self.wBomb//2) > 0 and ry - (self.hBomb//2) > 0 and bx != rx and by != ry):
                self.randomBombLoc()
                bx,by = self.bombPoint
            cvzone.putTextRect(imgMain,f'Score: {self.score}',[50,80],scale=2,thickness=2,font = cv2.FONT_HERSHEY_PLAIN)
            imgMain = cvzone.overlayPNG(imgMain,self.imgFood,(rx - (self.wFood//2),ry - (self.hFood//2) ))
            imgMain = cvzone.overlayPNG(imgMain,self.imgBomb,(bx - (self.wBomb//2),by - (self.hBomb//2) ))
        return imgMain

game = SnakeGame()
while True:
    success, img= cap.read()
    img = cv2.flip(img, 1)
    hands,img = detector.findHands(img, flipType=False)
    if hands:
        lmList = hands[0]["lmList"]
        pointIndex = lmList[8][0:2]
        img = game.update(img,pointIndex)
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('x'):
        break
    if key == ord('r'):
        game.gameOver = False