from PIL import Image, ImageTk

import numpy as np
import dlib
import math, time, os 
import cv2

def convert_shape(shape):
	a = np.zeros((68,2), dtype="int")
	for i in range(0,68):
		a[i] = (shape.part(i).x, shape.part(i).y)
	return a


def drawLandmarks(image, points):
    for point in points:
        x,y = point
        cv2.circle(image, (x,y),2,(255,0,0),-1)

# returns 68x2 array of predicted landmark points on frame
def getLandmarks(frame, detector, predictor):
    #higher == faster, but less accurate   
    scaleFactor = 1.08
    # higher == more accurate detection 
    minNeighbors = 5 
    detectedFace = detector.detectMultiScale(frame, scaleFactor, minNeighbors)
    x, y, w, h = 500, 200, 400, 400
    # if detector fails to detect face at this frame,
    # use a default rectangular box instead as a last-ditch attempt 
    if detectedFace != ():
        detectedFace = detectedFace[0]
        x, y, w, h = detectedFace[0], detectedFace[1], detectedFace[2], detectedFace[3]
    else:
        print("Face not detected, using DEFAULT")
    rects = dlib.rectangle(x,y,x+w,y+h)
    points = predictor(frame, rects)
    return convert_shape(points) 

def drawEyeRectangle(image, rec):
    color = (0,255,0)
    thickness = 2
    cv2.rectangle(image, rec[0], rec[1], color, thickness)

def rectangulateEye(image, points, boxWidth, boxHeight):
    #left = [37, 38, 39, 40, 41, 42]
    #right = [43, 44, 45, 46, 47, 48]
    leftL, rightL, upL, downL = (points[36][0], points[39][0], (points[37][1]+points[38][1])//2, 
            (points[40][1]+points[41][1])//2) 
    leftR, rightR, upR, downR = (points[42][0], points[45][0], (points[43][1]+points[44][1])//2, 
            (points[46][1]+points[47][1])//2) 
    cxL, cyL = (leftL+rightL)//2, (upL+downL)//2
    cxR, cyR = (leftR+rightR)//2, (upR+downR)//2
    x1L, y1L = cxL - boxWidth//2, cyL - boxHeight//2
    x2L, y2L = cxL + boxWidth//2, cyL + boxHeight//2
    x1R, y1R = cxR - boxWidth//2, cyR - boxHeight//2
    x2R, y2R = cxR + boxWidth//2, cyR + boxHeight//2 
    recR = ((x1R,y1R),(x2R,y2R))
    recL = ((x1L,y1L),(x2L,y2L))
    return recR, recL

def lcd(a, b, test=2):
    if test > a or test > b:
        print(a,b)
        return None
    elif a % test == 0 and b % test == 0:
        return test
    else:
        return lcd(a,b,test+1)

# returns chunk of 2D array as explicated by start, stop of
# row and col values. Both start, stop values inclusive in chunk
def getArrayChunk(image,rowStart,rowStop,colStart,colStop):
    chunk = []
    for row in image[rowStart:rowStop+1]:
        chunk.append(row[colStart:colStop+1])
    return chunk

def reverse2DList(L):
    reversedList = []
    for row in L:
        reversedList.append(row[::-1])
    return reversedList

def getPupil(eye, xstart, xstop, ystart, ystop, side=None):
    eyeSearch = getArrayChunk(eye, ystart, ystop, xstart, xstop)
    rows, cols = len(eyeSearch), len(eyeSearch[0])
    if side == None:
        side = lcd(cols, rows)
    pupilX, pupilY = getHighestSum(eyeSearch, rows, cols, side) 
    # account for area not included in eyesearch but
    # still part of eye
    pupilX += xstart
    pupilY += ystart
    pupilCx, pupilCy = pupilX - side//2, pupilY - side//2
    return pupilCx, pupilCy

def getHighestSum(gray, rows, cols, side):
    highest = float('-inf')
    highestX, highestY = None, None
    for yStep in range(1,rows//side+1):
        for xStep in range(1,cols//side+1):
            thisX, thisY = int(xStep*side), int(yStep*side)
            e = time.time()
            thisSum = sumArea(gray,thisX,thisY,1,side,side)
            s = time.time()
    #        print(s-e)
            if thisSum > highest:
                highest = thisSum
                highestX,highestY = thisX, thisY 
    return highestX, highestY
    
# given points A, B, C, D that form a rectangle 
# given points A, B, C, D that form a rectangle 
# with A, D as upper-left and lower-right corner 
# vertices, rspectively, area of rectangle can be
# found using sum (where sum == sum of all points
# to the left of D  that has a y value greater than
# D's), where area = sum(D) + sum(A) - sum(C) - sum(B) 
# Note sum(A) is added because it is double-accounted
# for during sum(C) and sum(B) 
def sumArea(gray,x,y,depth,width,height):
    if depth == 0:
        sumIntensities = 0 
        for y in range(y): 
            sumIntensities += sum(gray[y][:x+1])
        return sumIntensities
    else:
        Cx, Cy = x-width, y
        Bx, By = x, y-height
        Ax, Ay = x-width, y-height
        # ??? why None for width & height? 
        return (sumArea(gray,x,y,depth-1,None,None) + sumArea(gray,
            Ax, Ay, depth-1,None,None) - sumArea(gray,Cx,Cy,depth-1,None,None)
            - sumArea(gray,Bx,By,depth-1,None,None))


def flattenList(L):
    new = []
    for row in L:
        for elem in row:
            new.append(elem)
    return new

def avg2List(A,B):
    avg = []
    length = len(A)
    for i in range(length):
        avg.append((A[i]+B[i])/2)
    return avg

def processEyes(right,left):
    right = flattenList(right)    
    left = flattenList(left)
    avg = avg2List(right,left) 
    return avg
   
def arrayToImage(array):
    # convert color to RGB, from default BGR of openCV image
    array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    # flip image
    pil_image = Image.fromarray(array)
    pil_image = ImageTk.PhotoImage(pil_image)
    return pil_image

# in# def calibration points
def addCalibrationpointsToImage(app):
    # 5 alternating A, B types of calibration lines
    # A type:
    # 10% DOT 40% DOT 40% DOT 10%
    
    # B type:
    # 33% DOT 33% DOT 33%
    
    cols = len(app.image[0])
    segment = cols // 6 
    '''
    for i in range(1,6):
        if i % 2 != 0:
            drawTypeA(app, int(segment*i))
        else:
            drawTypeB(app, int(segment*i))
    '''
    rows = len(app.image)
    drawTypeC(app, int(rows*0.1))
    drawTypeC(app, int(rows*0.5))
    drawTypeC(app, int(rows*0.9))

def drawTypeA(app,xStart):
    rows = len(app.image)  
    dot1Y = int(rows * 0.1)
    dot2Y = int(dot1Y + rows * 0.4)
    dot3Y = int(dot2Y + rows * 0.4)
    cv2.circle(app.image, (xStart,dot1Y), 5, (255,255,0),-1)
    cv2.circle(app.image, (xStart,dot2Y), 5, (255,255,0),-1)
    cv2.circle(app.image, (xStart,dot3Y), 5, (255,255,0),-1)

def drawTypeB(app,xStart):
    rows = len(app.image)
    dot1Y = int(rows * 0.33)
    dot2Y = int(dot1Y + rows * 0.33)
    cv2.circle(app.image, (xStart, dot1Y), 5, (255,255,0), -1)
    cv2.circle(app.image, (xStart, dot2Y), 5, (255,255,0), -1)

def drawTypeC(app,yStart):
    cols = len(app.image[0])
    cv2.circle(app.image, (int(cols*0.1),yStart), 5, (255,255,0), -1)
    cv2.circle(app.image, (int(cols*0.5),yStart), 5, (255,255,0), -1)
    cv2.circle(app.image, (int(cols*0.9),yStart), 5, (255,255,0), -1) 

# add to image array using cv2
def addFeaturesToImage(app):
    drawLms(app.image,app.landmarks)
    drawEyeRec(app.image,app.rightEye)
    drawEyeRec(app.image,app.leftEye)
    '''
    cv2.circle(app.image, app.rightPupilCenter, 2, (0,0,255), 1)
    cv2.circle(app.image, app.leftPupilCenter, 2, (0,0,255), 1)
    '''
    if isinstance(app.gazePrediction, np.ndarray):
        gx,gy = app.gazePrediction
        gx, gy = int(gx), int(gy)
        cv2.circle(app.image, (gx,gy), 20, (255,0,0),1)


def drawLms(image,points):
    for point in points:
        x,y = point
        cv2.circle(image,(x,y),2,(255,0,0),-1)

def drawEyeRec(image,rec):
    color = (0,255,0) 
    thickness = 2
    cv2.rectangle(image, rec[0], rec[1], color, thickness)
    
