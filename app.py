##################################################
# MINJUNE SONG Term Project
################################################## 

##################################################
#modules
##################################################

from cmu_112_opencv_graphics import *
#from PIL import Image, ImageTk
import dlib
import cv2
import numpy as np

# python modules
import math, time, os, random, json

# my modul;es
import utils 
import reg_utils as reg

# MODES:
# login, signup, home, calibrate, focus, session, analytics

# app first opened:
# redirect to LOGIN Screen. 
# proceeds only to HOME screen when LOGIN fulfilled.

USR = "users"

##################################################
# helper methods
##################################################

def clear(canvas):
    gridObjs = canvas.grid_slaves()
    for obj in gridObjs:
        obj.destroy()

# code from: https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html
def removeTempFiles(path, suffix='.DS_Store'):
    if path.endswith(suffix):
        print(f'Removing file: {path}')
        os.remove(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            removeTempFiles(path + '/' + filename, suffix)
        
##################################################
# login MODE
##################################################

def appStarted(app):
    init_login(app)
    

def init_login(app):
    app.mode = "login"
    app.usr = StringVar()
    app.psw = StringVar()
    app.click = None
    app.thisDir = os.getcwd()
    app.usrPath = app.thisDir + '/' + "users" 
    removeTempFiles(app.usrPath)
    app.currentUserFileName = None
    #app.loginList = getUsers(app)

    # button 
    app.login_signUpButtonCx = app.width/2
    app.login_signUpButtonCy = 550
    app.login_signUpButtonRadius = 30

    # Logo
    app.login_logoCx, app.login_logoCy = app.width/2,app.height/2
    app.login_logoRadius = 70
    removeTempFiles(app.thisDir + '/sessions')
    removeTempFiles(app.thisDir + '/users')

# use dubious
def getUsers(app):
    logins = []
    for obj in os.listdir(app.usrPath):
        firstLine = getFirstLine(app,obj)
        firstLine = firstLine.split(",")
        usr, psw = firstLine[0], firstLine[1]
        logins.append((usr, psw))
    return logins

def getFirstLine(app,target):
    filePath = os.path.join(app.usrPath, target)
    with open(filePath) as f:
        firstLine = f.readline().rstrip()
    return firstLine

def login_keyPressed(app, event):
    if event.key == "Enter":
        if credentialsValid(app):
            print('login success')
            app.mode = 'home'
            init_home(app)
        else:
            print('login failed')

def credentialsValid(app):
    # retrieve username/passwords of users
    username = app.usr.get()
    password = app.psw.get()

    for obj in os.listdir(app.usrPath):
        if obj[-4:] == '.npy': continue
        firstLine = getFirstLine(app,obj)
        firstLine = firstLine.split(",")
        usr, psw = firstLine[0], firstLine[1]
        if (usr, psw) == (username, password):
            app.currentUserFileName = obj
            return True
    return False 

def login_mousePressed(app, event):
    app.click = (event.x, event.y)
    # when signup clicked
     
    if inCircle(app.login_signUpButtonCx,app.login_signUpButtonCy,
            event.x, event.y,app.login_signUpButtonRadius ):
        init_signup(app)
        app.mode = 'signup'

def login_redrawAll(app,canvas):
    # login entry padding top 
    canvas.grid_columnconfigure(0,weight=1)
    canvas.grid_rowconfigure(0,weight=1)
    canvas.grid_rowconfigure(1,weight=1)
    # login entry
    usrEntry = Entry(canvas,textvariable = app.usr, font=('calibre',10,'normal'))
    usrEntry.grid(row=2,column=1)
    pswEntry = Entry(canvas, textvariable = app.psw, font = ('calibre',10,'normal'),
            show = '*')
    pswEntry.grid(row=3,column=1)
    # login entry padding buttom
    canvas.grid_rowconfigure(4,weight=1)
    canvas.grid_columnconfigure(2,weight=1)


    # buttons
    canvas.create_rectangle(720, 450, 770, 468)
    canvas.create_rectangle(720, 475, 770, 493)
    canvas.create_text(745, 459, text='username', font='Hevetica 9 bold', fill='black')
    canvas.create_text(745, 484, text='password', font='Hevectica 9 bold', fill='black')
    
    # login button

    # write signup credentials label 
    r =  app.login_signUpButtonRadius
    cx, cy = app.login_signUpButtonCx, app.login_signUpButtonCy
    canvas.create_oval(cx-r,cy-r,cx+r,cy+r) 
    canvas.create_text(cx, cy, text='sign up', font='Helvetica 12 bold')


    # logo 
    cx = app.login_logoCx
    cy = app.login_logoCy
    r = app.login_logoRadius
    canvas.create_oval(cx+r,cy+r, cx-r,cy-r,fill='black')
    canvas.create_arc(cx+r,cy+r, cx-r, cy-r, start=180, extent=180,fill='white')



##################################################
# signup mode
##################################################

def init_signup(app):
    app.drawn = False
    app.newUsr = StringVar()
    app.newPsw = StringVar()
    app.signup_errorMsg = None

    # buttons 
    app.signup_registerButtonCx = app.width/2
    app.signup_registerButtonCy = app.login_signUpButtonCy
    app.signup_registerButtonRadius = app.login_signUpButtonRadius



def signup_mousePressed(app, event):
    if inCircle(app.signup_registerButtonCx, app.signup_registerButtonCy, 
            event.x, event.y, app.signup_registerButtonRadius):
        usr, psw = app.newUsr.get(), app.newPsw.get()
        if not isRegistered(app, usr, psw):
            registerNew(app, usr, psw)
            init_login(app)
            app.mode = 'login'
        else:
            app.signup_errorMsg = 'already registered user!'

# register new user (create new file)
def isRegistered(app, usr, psw):
    for login in os.listdir(app.usrPath):
        if login[-4:] == '.npy': continue
        print(login[-4:])
        filePath = os.path.join(app.usrPath, login)
        with open(filePath) as f:
            line = f.readline().rstrip()
            line = line.split(",")
            if usr == line[0] and psw == line[1]:
                return True
    return False

def registerNew(app, usr, psw):
    # create new text file that registers user
    fileNum =  len(os.listdir(app.usrPath)) 
    fileName = 'user'+str(fileNum)
    filePath = os.path.join(app.usrPath, fileName)
    credentials = str(usr) + ',' + str(psw)
    with open(filePath, 'w') as newFile:
        newFile.write(credentials)

def signup_keyPressed(app,event):
    if event.key == 'Escape':
        init_login(app)
        app.mode = 'login'

def signup_timerFired(app):
    if not app.drawn:
        app.drawn = True

def signup_redrawAll(app,canvas):
    if not app.drawn:
        clear(canvas)
    # login entry padding top 
    canvas.grid_columnconfigure(0,weight=1)
    canvas.grid_rowconfigure(0,weight=1)
    canvas.grid_rowconfigure(1,weight=1)
    # login entry
    usrEntry = Entry(canvas,textvariable = app.newUsr, font=('calibre',10,'normal'))
    usrEntry.grid(row=2,column=1)
    pswEntry = Entry(canvas, textvariable = app.newPsw, font = ('calibre',10,'normal'),
            show = '*')
    pswEntry.grid(row=3,column=1)
    # login entry padding buttom
    canvas.grid_rowconfigure(4,weight=1)
    canvas.grid_columnconfigure(2,weight=1)

    ################################################## 
    # buttons
    ##################################################

    # logo
    cx = app.login_logoCx
    cy = app.login_logoCy
    r = app.login_logoRadius
    canvas.create_oval(cx+r,cy+r, cx-r,cy-r,fill='black')
    canvas.create_arc(cx+r,cy+r, cx-r, cy-r, start=180, extent=180,fill='white')

    # username, password label
    canvas.create_rectangle(720, 450, 820, 468)
    canvas.create_rectangle(720, 475, 820, 493)
    canvas.create_text(770, 459, text='create_username', font='Hevetica 9 bold', fill='black')
    canvas.create_text(770, 484, text='create_password', font='Hevectica 9 bold', fill='black')

    # register button
    r = app.signup_registerButtonRadius
    cx, cy = app.signup_registerButtonCx, app.signup_registerButtonCy
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r) 
    canvas.create_text(cx, cy, text='register', font='Helvetica 12 bold')

    if app.signup_errorMsg != None:
        canvas.create_text(app.width/2, app.height/2, text=app.signup_errorMsg, font='Hevectica 36 bold',
                fill = 'black')

##################################################
# home screen MODE
##################################################

def init_home(app):
    app.drawn = False

    # calibration preview
    app.capture = None
    try:
        app.capture = cv2.VideoCapture(0)
    except:
        raise Exception("no camera found")
    app.image = []
    app.fireDelay = 33
    app.detector = cv2.CascadeClassifier("resources/haar_default.xml")
    app.predictor = dlib.shape_predictor("resources/shape_predictor_68_face_landmarks.dat")
    app.recWidth, app.recHeight = 75, 35 



    # load Calibration button
    app.home_loadButtonCx = app.width/2
    app.home_loadButtonCy = app.height/2
    app.home_loadButtonRadius = 50

    app.userCalibration = None
    app.calibrationLoaded = False
    app.calibrationRemind = False

    # buttons for calibration, focus, analytics
    app.home_buttonMargin = 20
    app.home_buttonSpan = app.width*0.6 / 3
    app.home_calibrateButtonCx = app.width*0.2
    app.home_calibrateButtonCy = app.height*0.1
    app.home_focusButtonCx = app.home_calibrateButtonCx + app.home_buttonSpan
    app.home_focusButtonCy = app.height*0.1
    app.home_analyticsButtonCx = app.home_calibrateButtonCx + 2*app.home_buttonSpan
    app.home_analyticsButtonCy = app.height*0.1

    app.userCoef = None
    app.userIntercept = None




def home_keyPressed(app,event):
    if event.key == 'c':
        app.mode = 'calibrate'
        init_calibrate(app)
    elif event.key == 'f':
        app.mode = 'focus'
        init_focus(app)
    elif event.key == 'a':
        app.mode = 'analytics'
        init_analytics(app)
    elif event.key == 'p':
        init_palette(app)
        app.mode = 'palette'

def userSavedCalibration(app):
    potentialCoefFile = app.currentUserFileName + 'Coef.npy' 
    potentialInterceptFile = app.currentUserFileName + 'Intercept.npy'
    potentialFiles = os.listdir(app.usrPath)
    return potentialCoefFile in potentialFiles and potentialInterceptFile in potentialFiles

def loadUserCalibration(app):
    coefFileName = app.currentUserFileName + 'Coef.npy'
    interceptFileName = app.currentUserFileName + 'Intercept.npy'
    userCoefPath = os.path.join(app.usrPath,coefFileName)
    userInterceptPath = os.path.join(app.usrPath,interceptFileName)
    app.userCoef = np.load(userCoefPath)
    app.userIntercept = np.load(userInterceptPath)


def home_timerFired(app):
    if not app.drawn:
        app.drawn = True
    if app.calibrationLoaded:
        # do not need to actually paint eyeChunk into image
        # do not need to actually paint eyeChunk into image
        _, frame = app.capture.read()
        image = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lms = utils.getLandmarks(frame, app.detector, app.predictor)
        recR, recL = utils.rectangulateEye(frame, lms, app.recWidth, app.recHeight) 
        rightEyeChunk = utils.getArrayChunk(frame,recR[0][1],recR[1][1],recR[0][0],recR[1][0])
        leftEyeChunk = utils.getArrayChunk(frame,recL[0][1],recL[1][1],recL[0][0],recL[1][0])
        X = utils.processEyes(rightEyeChunk, leftEyeChunk) 
        gazePrediction = reg.predictWithCoef(X, app.userIntercept, app.userCoef)

        image = cv2.flip(image,1)
        gx, gy = gazePrediction
        gx, gy = int(gx), int(gy) 
        # add to image 
        cv2.circle(image, (gx,gy), 20, (255,0,0), -1)

        # rescale image 
        image = rescaleImage(image,60)
        # transform to photoImage
        app.image = utils.arrayToImage(image)

def rescaleImage(image,scale):
    width = int(scale/100 * image.shape[1])
    height = int(scale/100 * image.shape[0])
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return image

def home_mousePressed(app,event):
    # buttons for Calibrate, Focus, Analytics
    span = app.home_buttonSpan
    margin = app.home_buttonMargin
    if inCircle(app.home_loadButtonCx, app.home_loadButtonCy,
            event.x, event.y, app.home_loadButtonRadius):
        if userSavedCalibration(app):
            app.calibrationRemind = False
            loadUserCalibration(app)
            app.calibrationLoaded = True
        else:
            app.calibrationRemind = True  
    elif inRectangle(app.home_calibrateButtonCx, app.home_calibrateButtonCy,
            app.home_calibrateButtonCx+span, app.home_calibrateButtonCy+margin,
            event.x, event.y):
        # do calibrate event
        init_calibrate(app)
        app.mode = 'calibrate'
    elif inRectangle(app.home_focusButtonCx, app.home_focusButtonCy, 
            app.home_focusButtonCx+span, app.home_focusButtonCy+margin,
            event.x, event.y):
        # do focus event
        init_focus(app)
        app.mode = 'focus'
    elif inRectangle(app.home_analyticsButtonCx, app.home_analyticsButtonCy,
            app.home_analyticsButtonCx+span, app.home_analyticsButtonCy+margin,
            event.x, event.y):
        if len(os.listdir(app.thisDir + '/' + 'sessions'))>0:
        # do analytics
            init_analytics(app)
            app.mode = 'analytics'

def home_redrawAll(app,canvas):
    if not app.drawn:
        clear(canvas) 
    # UI for mode boxes
    margin = app.home_buttonMargin
    span = app.home_buttonSpan

    cx,cy = app.home_calibrateButtonCx, app.home_calibrateButtonCy
    canvas.create_rectangle(cx,cy,cx+span,cy+margin)
    canvas.create_text(cx+span/2,cy+margin/2,text='calibrate',font='Helvetica 12 bold', fill='black')

    cx,cy = app.home_focusButtonCx, app.home_focusButtonCy
    canvas.create_rectangle(cx,cy,cx+span,cy+margin)
    canvas.create_text(cx+span/2,cy+margin/2,text='focus',font='Helvetica 12 bold', fill='black')

    cx,cy = app.home_analyticsButtonCx, app.home_analyticsButtonCy
    canvas.create_rectangle(cx,cy,cx+span,cy+margin)
    canvas.create_text(cx+span/2,cy+margin/2,text='analytics',font='Helvetica 12 bold', fill='black')

    # button for loading user-specific calibration
    cx, cy = app.home_loadButtonCx, app.home_loadButtonCy
    r = app.home_loadButtonRadius
    canvas.create_oval(cx - r , cy -r, cx + r, cy + r)    
    canvas.create_text(cx, cy, text='load calibration', font='Helvetica 14 bold',
            fill='black')
    
    if app.calibrationRemind:
        canvas.create_text(cx,cy,text='missing calibration for user', font='Helvetia 36 bold',
                fill='black')

    if app.calibrationLoaded:
        try:
            canvas.create_image(app.width/2, app.height*0.6, image=app.image)
        except:
            pass


    


##################################################
# calibrate screen MODE

# ideas: instead of having fixed calibration dots, 
# make an algorithm that makes dot pop-up and
# gets user to click it until it dissapears (5-10 times)
# train that way. 
##################################################

def init_calibrate(app):
    app.capture = None
    try:
        app.capture = cv2.VideoCapture(0)
    except:
        raise Exception("no camera found")
    app.image = []
    app.fireDelay = 33
    app.detector = cv2.CascadeClassifier("resources/haar_default.xml")
    app.predictor = dlib.shape_predictor("resources/shape_predictor_68_face_landmarks.dat")
    app.recWidth, app.recHeight = 75, 35 
    app.totalClicks = []
    # if batchPotential > batchThreshold, collect [-batchThreshold:] 
    # click objects in totalClicks and use them as resutls, 
    # do same for trainBatch
    app.batchThreshold = 45 
    app.batchPotential = 0

    app.trainBatch = {}
    app.coef = None 
    app.intercept = None

    # draw objects
    app.landmarks = None
    app.rightEye = None
    app.leftEye = None
    app.rightEyeChunk = None
    app.leftEyeChunk = None
    app.rightPupilCenter = None
    app.leftPupilCenter = None

    # UI logistics of calibration 
    app.gazePrediction = None
    # calibrationPoints can only be added when app.image != None
    app.calibrationPoints = None
    app.calibrationPointsRadius = 5

    # buttons
    # calibration save button
    app.calibrationSaveButtonX = app.width * 0.4
    app.calibrationSaveButtonY = app.height *0.5
    app.calibrationSaveButtonRadius = 100

    # calibration exit button
    app.calibrationExitButtonX = app.width * 0.6
    app.calibrationExitButtonY = app.height * 0.5
    app.calibrationExitButtonRadius = 100

    
# create a record of all the corresponding x,y positions on
# canvas of calibration points the user will click on. 
def makeCalibrationPointsDict(rows, cols, margin, seperation, limit=5):
    pointSet = dict()
    yPositions = [rows*margin, rows*(margin+seperation), rows*(margin+2*seperation)]
    xPositions = [cols*margin, cols*(margin+seperation), cols*(margin+2*seperation)]
    for y in yPositions:
        for x in xPositions: 
            pointSet[(int(x), int(y))] = limit 
    return pointSet

# add calibration points to image array

def addCalibrationPointsToImage(app):
    colors = [(255,73,0),(255,243,0),(0,255,182),(66,0,255),(255, 207, 224)]
    #colors = ['#00FFFB', '#4BFFFC', '#96FFFD',"#C8FFFE','transparent']
    for pointKey in app.calibrationPoints.keys():
        colorIndex = (app.calibrationPoints[pointKey]) * -1
        colorIndex = int(colorIndex)
        if colorIndex >= 0: continue
        else:
            cv2.circle(app.image, (pointKey), app.calibrationPointsRadius,
                    colors[colorIndex], -1)

def calibrationSaveDataToUser(app, data):
    currentUser = app.currentUserFileName
    # ex: user0Coef.npy
    currentUserCoef = currentUser +'Coef' + '.npy'
    # ex: user0Intercept.npy
    currentUserIntercept = currentUser + 'Intercept' + '.npy'
    currentUserCoefPath = os.path.join(app.usrPath, currentUserCoef) 
    currentUserInterceptPath = os.path.join(app.usrPath, currentUserIntercept)
    np.save(currentUserCoefPath,data[0], allow_pickle=True) 
    np.save(currentUserInterceptPath,data[1], allow_pickle=True)

def calibrate_keyPressed(app, event):
    if event.key == 'Escape':
        init_home(app)
        app.mode = 'home'

def calibrate_mousePressed(app,event):
    if isinstance(app.coef, np.ndarray):
        if inCircle(app.calibrationSaveButtonX, app.calibrationSaveButtonY, event.x, event.y,
                app.calibrationSaveButtonRadius):
            # save calibration trained data
            # then exit
            calibrationSaveDataToUser(app, (app.coef, app.intercept))
            app.mode = 'home'
        elif inCircle(app.calibrationExitButtonX, app.calibrationExitButtonY, event.x, event.y,
                app.calibrationExitButtonRadius):
            # exit without saving
            app.mode = 'home'
    elif app.calibrationPoints != None:
        for pointKey in app.calibrationPoints.keys():
            x, y = pointKey[0], pointKey[1]
            if (inCircle(x,y,event.x,event.y,app.calibrationPointsRadius) 
            and app.calibrationPoints[pointKey] > 0): 
                # batch training logistics
                currClick = (event.x, event.y)
                app.batchPotential += 1
                if app.batchPotential < app.batchThreshold: 
                   app.trainBatch[currClick] = (
                       (app.rightEyeChunk, app.leftEyeChunk))
                else:
                    app.trainBatch[currClick] = (
                        (app.rightEyeChunk, app.leftEyeChunk)
                    )
                    trainEyesOnClicks(app)
                    app.batchPotential = 0
                    app.trainBatch = dict()
                # user display logistics
                # reduce number of presses user must do 
                app.calibrationPoints[pointKey] -= 1


def trainEyesOnClicks(app):
    X, Y = [], []
    for k in app.trainBatch.keys():
        # Key == x,y position of click 
        # Value == eye pixels at click  
        y = [k[0], k[1]]
        Y.append(y)
        v = app.trainBatch[k]
        rightEye, leftEye = v[0], v[1]
        processedX = utils.processEyes(rightEye, leftEye)
        # if Y dims == (1,2), then X dims == (1,2---)
        X.append(processedX)

    currentCoefs, currentIntercept = reg.getParams(X,Y)

    if not isinstance(app.coef, np.ndarray):
        app.coef = currentCoefs
        app.intercept = currentIntercept
    else:
        avgCoef = utils.avg2List(currentCoefs, app.coef)
        avgIntercept = utils.avg2List(currentIntercept, app.intercept)
        avgCoef = np.array(avgCoef)
        avgIntercept = np.array(avgIntercept)
        app.coef = avgCoef
        app.intercept = avgIntercept

def calibrate_timerFired(app):
    _, frame = app.capture.read()
    app.image = frame.copy()

    # only is called once
    if app.calibrationPoints == None:
            app.calibrationPoints = makeCalibrationPointsDict(
            len(app.image), len(app.image[0]), 0.1, 0.4, 5)


    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lms = utils.getLandmarks(frame, app.detector, app.predictor)
    recR, recL = utils.rectangulateEye(frame, lms, app.recWidth, app.recHeight) 

    # optional: add pupil center
    
    rightEyeChunk = utils.getArrayChunk(frame,recR[0][1],recR[1][1],recR[0][0],recR[1][0])
    leftEyeChunk = utils.getArrayChunk(frame,recL[0][1],recL[1][1],recL[0][0],recL[1][0])

    app.rightEye = recR
    app.leftEye = recL
    app.rightEyeChunk = rightEyeChunk
    app.leftEyeChunk = leftEyeChunk
    app.landmarks = lms

    if isinstance(app.coef, np.ndarray): 
        #print('coef',app.coef, 'intercept', app.intercept)
        X = utils.processEyes(rightEyeChunk, leftEyeChunk) 
        app.gazePrediction = reg.predictWithCoef(X, app.intercept, app.coef)
        gx, gy = app.gazePrediction
        #print(f'predicting gaze --> (x:{gx},y:{gy})')
    else:
        # add features to image
        utils.addFeaturesToImage(app)
        addCalibrationPointsToImage(app)
        app.image = utils.arrayToImage(app.image)

        

def calibrate_redrawAll(app,canvas):
    if isinstance(app.coef, np.ndarray):
        # create calibration + save and exit button
        cx,cy = app.calibrationSaveButtonX, app.calibrationSaveButtonY
        radius = app.calibrationSaveButtonRadius
        canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius)
        canvas.create_text(cx,cy,text='save',font='Helvetica 36 bold',fill='black')

        # create calibration + no save exit button
        cx,cy = app.calibrationExitButtonX, app.calibrationExitButtonY
        radius = app.calibrationExitButtonRadius
        canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius)
        canvas.create_text(cx,cy,text='exit',font='Helvetica 36 bold',fill='black')
    else:
        try:
            canvas.create_image(app.width/2,app.height/2,image=app.image)
        except:
            pass


##################################################
# focus create MODE
# components:
# Name, begin-time, end-time, color, description
# user must fill in all before beginning
# once BEGIN SESSION  pressed: 
# 1) show On icon as background for (end-time - begin-time) duration
# 2) Save Name, time, color, description as X file into USR profile
##################################################

def init_focus(app):
    app.focus_name = StringVar()
    app.focus_time = StringVar()
    # figure out how to  do color palette selector (later)
    app.focus_desc = StringVar()
    app.sessionPath = app.thisDir + '/' + 'sessions'

    # focus AREA should be defined
    
    # focus buttons

    # load calibration data button
    app.focus_beginButtonCx, app.focus_beginButtonCy = app.width/2,550
    app.focus_beginButtonRadius = 30

    app.focus_displayErrorMsg = False
    
def focus_keyPressed(app,event):
    if event.key == 'Escape':
        init_home(app)
        app.mode = 'home'
    print(event.key)

def inCircle(cx,cy, x,y, r):
    return ((cx-x)**2 + (cy-y)**2)**0.5 <= r

# BEGIN SESSION BUTTON
def focus_mousePressed(app,event):
    app.click = (event.x, event.y)
    if inCircle(app.focus_beginButtonCx,app.focus_beginButtonCy, event.x, event.y, 
            app.focus_beginButtonRadius):
        # begin only if user loaded their parameters that they have previously
        # calibrated
        if app.calibrationLoaded:
            saveSession(app)
            #init_session(app)
            #app.mode = 'session'
            init_palette(app)
            app.mode = 'palette'
        else:
            app.focus_displayErrorMsg = True

def saveSession(app):
    sessionNum = len(os.listdir(app.sessionPath))
    print(os.listdir(app.sessionPath))
    print(sessionNum)
    sessionName = 'session' + str(sessionNum)
    sessionFile = os.path.join(app.sessionPath, sessionName)

    # info to be written
    name = app.focus_name.get()
    time = app.focus_time.get()
    desc = app.focus_desc.get()

    with open(sessionFile, 'w') as newSession:
        newSession.write('name,'+name + '\n')
        newSession.write('time,'+time + '\n')
        newSession.write('desc,'+desc + '\n')

# FOCUS
 
def focus_redrawAll(app,canvas):

    # <add labels>

    # name label
    cx, cy = 815,320
    w = 50
    h = 18
    canvas.create_rectangle(cx, cy, cx+w, cy+h)
    canvas.create_text(cx+w/2, cy+h/2, text='name', font='Helvetica 9 bold')
    # time begin-end label

    cy = 412
    canvas.create_rectangle(cx, cy, cx+w, cy+h)
    canvas.create_text(cx+w/2, cy+h/2, text='time', font='Helvetica 9 bold')
    # desc label

    w = 100
    cy = 442
    canvas.create_rectangle(cx, cy, cx+w, cy+h) 
    canvas.create_text(cx+w/2, cy+h/2, text='description', font='Helvetica 9 bold')

    # begin session label
    r = app.focus_beginButtonRadius
    cx,cy = app.focus_beginButtonCx,app.focus_beginButtonCy
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r) 
    canvas.create_text(cx, cy, text='begin', font='Helvetica 12 bold')

    focus_name = Entry(canvas,textvariable = app.focus_name, font='Helvetica 14 bold',width=40) 
    begin_time = Entry(canvas, textvariable = app.focus_time, font='Helvetica 14 bold',width=40)
    desc = Entry(canvas, textvariable = app.focus_desc, font='Helvetica 14 bold', width=40)

    focus_name.grid(row=1, column = 1)
    begin_time.grid(row=2, column = 1)
    desc.grid(row=3, column = 1)

    # add spacing
    canvas.grid_rowconfigure(0, weight=2)
    canvas.grid_rowconfigure(4, weight=2)
    canvas.grid_columnconfigure(0, weight=1)
    canvas.grid_columnconfigure(2, weight=1)

    # individually configure sizes of focus, begin, end, desc 

    # name

    # time

    # desc
    if app.click != None:
        canvas.create_text(100, 200, text=f'{app.click[0], app.click[1]}',
                font='Hevetica 12 bold', fill='black')
    if app.focus_displayErrorMsg:
        canvas.create_text(app.width/2,app.height/2,text='No Existing Calibration',
                font='Hevetica 36 bold', fill='red')


##################################################
# palette MODE, where users can specify the area of screen
# they wish to focus most on 
##################################################

def init_palette(app):
    app.drawn = False
    app.paletteClicked = False
    app.stopMouseTrack = False
    app.paletteBegin = None 
    app.paletteEnd = None

    # buttons
    app.palette_redrawButtonCx = app.width/2
    app.palette_redrawButtonCy = app.height*0.1
    app.palette_redrawDims = 60, 20


    app.palette_startButtonCx = app.width/2
    app.palette_startButtonCy = app.height*0.2
    app.palette_startDims = 60, 20

def palette_mousePressed(app, event):
    if not app.paletteClicked:
        app.paletteBegin = (event.x, event.y)
        app.paletteClicked = True
    else:
        if not app.stopMouseTrack:
            app.paletteEnd = (event.x, event.y)
            app.stopMouseTrack = True
    cx1,cy1 = app.palette_redrawButtonCx, app.palette_redrawButtonCy
    cx2,cy2 = app.palette_startButtonCx, app.palette_startButtonCy
    w,h = app.palette_redrawDims
    if inRectangle(cx1-w,cy1-h,cx1+w,cy1+h,event.x,event.y):
        app.paletteClicked = False
        app.stopMouseTrack = False
    elif inRectangle(cx2-w,cy2-h,cx2+w,cy2+h,event.x,event.y):
        init_session(app)
        app.mode = 'session'
# mouse moved, get exact def of 112 graphics
def palette_mouseMoved(app, event):
    if not app.stopMouseTrack:
        app.paletteEnd = (event.x, event.y)

def palette_keyPressed(app, event):
    if event.key == 'Escape':
        init_focus(app)
        app.mode = 'focus'

def palette_timerFired(app):
    if not app.drawn:
        app.drawn = True


def palette_redrawAll(app,canvas):
    if not app.drawn: 
        clear(canvas)

    cx, cy = app.palette_redrawButtonCx, app.palette_redrawButtonCy
    w, h = app.palette_redrawDims
    canvas.create_rectangle(cx-w, cy-h, cx+w, cy+h)
    canvas.create_text(cx, cy, text='select new area', font='Helvetica 14 bold', 
            fill = 'black')

    cx, cy = app.palette_startButtonCx, app.palette_startButtonCy
    w, h = app.palette_startDims
    canvas.create_rectangle(cx-w, cy-h, cx+w, cy+h)
    canvas.create_text(cx, cy, text='begin session', font='Helvetica 14 bold', 
            fill = 'black')

    if app.paletteBegin != None and app.paletteEnd != None:
        if app.paletteClicked:
            bx, by = app.paletteBegin
            ex, ey = app.paletteEnd
            canvas.create_rectangle(bx,by,ex,ey)


##################################################
# focus record MODE
# show ON icon, and end when time ends. 
##################################################

def init_session(app):
    # session capture logistics
    app.capture = None
    try:
        app.capture = cv2.VideoCapture(0)
    except:
        raise Exception("no camera found")
    app.image = []
    app.fireDelay = 33
    app.detector = cv2.CascadeClassifier("resources/haar_default.xml")
    app.predictor = dlib.shape_predictor("resources/shape_predictor_68_face_landmarks.dat")
    app.recWidth, app.recHeight = 75, 35 

    # length of session (milisec)
    if app.focus_time.get() != '' and app.focus_time.get().isdigit():
        app.sessionLimit = int(app.focus_time.get())*60
    else:
        # default == 10 sec
        app.sessionLimit = 60

    app.sessionLength = 0
    app.fireDelay = 33
    app.status = 'FOCUS'
    app.s = time.time() 
    app.stopButtonCx = app.width/2
    app.stopButtonCy = app.height/2
    app.stopButtonRadius = 50
    # arbitrary

    # set drawn to False again
    app.drawn = False
    print(app.paletteBegin, app.paletteEnd)

    # logistics for tracking analytic data
    #track ratio of prediction being in & out of user-set area per minute
    # currently, duration in terms of seconds. change this to duration in terms of minutes
    app.minuteTrack = createRecord(app.sessionLimit // 60)

def createRecord(duration):
    minuteTrack = dict()
    for minute in range(duration):
        minuteTrack[minute] = 0
    return minuteTrack

def saveSessionData(app, data, time):
    currentSessionNum = len(os.listdir(app.sessionPath)) - 1 
    currentSessionName = 'session' + str(currentSessionNum)
    currentSessionFile = os.path.join(app.sessionPath, currentSessionName)


    with open(currentSessionFile, 'a+') as currentSession:
        currentSession.write('time,'+str(time)+'\n')
        try:
            currentSession.write('data,'+json.dumps(data) + '\n')
        except:
            print('error saving data')

def session_keyPressed(app,event):
    if event.key == 'Escape':
        init_home(app)
        app.mode = 'home'
    elif app.status == 'DONE':
        saveSessionData(app, app.minuteTrack, app.sessionLength)
        init_home(app)
        app.mode = 'home'

    


def session_mousePressed(app,event):
    if inCircle(app.stopButtonCx, app.stopButtonCy, 
            event.x, event.y, app.stopButtonRadius):
        saveSessionData(app, app.minuteTrack, app.sessionLength)
        init_home(app)
        app.mode = 'home'

def inRectangle(x1,y1, x2, y2, x3, y3):
    if (x3 >= x1 and x3 <= x2) and (y3 >= y1 and y3 <= y2):
        return True
    else:
        return False

def addToTracker(app, gx, gy):
    minute = int(app.sessionLength // 60)
    x1, y1 = app.paletteBegin
    x2, y2 = app.paletteEnd
    if inRectangle(x1,y1,x2,y2,gx,gy):
        app.minuteTrack[minute]+=1

def session_timerFired(app):
    if not app.drawn:
        app.drawn = True
    if app.sessionLength < app.sessionLimit:
        # do not need to actually paint eyeChunk into image
        # do not need to actually paint eyeChunk into image
        _, frame = app.capture.read()
        image = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lms = utils.getLandmarks(frame, app.detector, app.predictor)
        recR, recL = utils.rectangulateEye(frame, lms, app.recWidth, app.recHeight) 
        rightEyeChunk = utils.getArrayChunk(frame,recR[0][1],recR[1][1],recR[0][0],recR[1][0])
        leftEyeChunk = utils.getArrayChunk(frame,recL[0][1],recL[1][1],recL[0][0],recL[1][0])
        X = utils.processEyes(rightEyeChunk, leftEyeChunk) 
        gazePrediction = reg.predictWithCoef(X, app.userIntercept, app.userCoef)
        gx, gy = gazePrediction
        gx, gy = int(gx), int(gy) 
        # add to image 
        cv2.circle(image, (gx,gy), 20, (255,0,0), -1)

        
        app.image = utils.arrayToImage(image)

        app.e = time.time()
        app.sessionLength = app.e-app.s

        # add to analytics
        addToTracker(app,gx,gy)
    else:
        app.status = 'DONE'
    

def session_redrawAll(app,canvas):
    # only clear canvas once (set drawn to True at first 
    # calling of timerFired
    if not app.drawn:
        clear(canvas)

    # stop session label
    r = app.stopButtonRadius 
    cx,cy = app.stopButtonCx, app.stopButtonCy
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r) 
    canvas.create_text(cx, cy, text='stop', font='Helvetica 36 bold')

    if app.status == 'FOCUS':
        try:
            canvas.create_image(app.width/2, app.height/2, image=app.image)
        except:
            pass
    else:
        canvas.create_text(app.width*0.3, app.height*0.3, text=f'{app.status}',
            font='Helvetica 64 bold', fill='black')

        canvas.create_text(app.width/2, app.height/2, text='click anywhere to go home',
                font='Helvetica 36 bold', fill='black')

##################################################
# analytics MODE
# display past user FOCUS session files 
# display data when clicked
##################################################

def init_analytics(app):
    app.drawn = False
    app.sessionPath = app.thisDir + '/' + 'sessions' 
    app.viewingSession = len(os.listdir(app.sessionPath)) - 1
    app.viewingSessionName = None
    app.viewingSessionTime = None
    app.viewingSessionDesc = None
    app.viewingSessionDuration = None
    app.minuteTrack = None
    loadSession(app)

    # temp

    # ~180 captures per minute
    # ration should be for any minute:
    # minuteTrack[minute] / 180
    #print(app.minuteTrack)
    app.elapsed = None

    # test minuteTrack
    
    #app.minuteTrack = testSet() 
    app.s = time.time()

    # data display
    app.analytics_xStart = app.width * 0.1
    app.analytics_yStart = app.height * 0.4
    app.analytics_xSpan = app.width * 0.8
    app.analytics_ySpan = app.height * 0.4

    app.analytics_nameCx, app.analytics_nameCy = app.width/2, app.height*0.05
    app.analytics_nameWidth, app.analytics_nameHeight = 20,15

    app.analytics_timeCx, app.analytics_timeCy = app.width/2, app.height*0.1
    app.analytics_timeWidth, app.analytics_timeHeight = 20,15

    app.analytics_descCx, app.analytics_descCy = app.width/2, app.height*0.2
    app.analytics_descWidth, app.analytics_descHeight = 20,15



def testSet():
    result = dict()
    for i in range(30):
        result[str(i)] = random.randint(100,500)
    return result

def loadSession(app):
    sessionNum = app.viewingSession
    sessionName = 'session' + str(sessionNum)
    sessionPath = os.path.join(app.sessionPath, sessionName)

    loadingSession = open(sessionPath,'r')
    lines = loadingSession.readlines()

    for line in lines: 
        thisLine = line.split(',')
        tag, content = thisLine[0], thisLine[1]
        if tag == 'name':
            app.viewingSessionName = content
        elif tag == 'time':
            app.viewingSessionTime = content
        elif tag == 'desc':
            app.viewingSessionDesc = content
        elif tag == 'data':
            content = thisLine[1]
            for piece in thisLine[2:]:
                content += ',' + piece
            print(content)
            content = json.loads(content)
            app.minuteTrack = content

# unpack minuteTrack values
# scale minuteTrack to width of app 
# draw a 10xminute grid that displays
# percentage of focus per minute across all recorded minutes
# as a histogram bar
# fill in the grid appropriately
def analytics_drawPlot(app, canvas):
    #minutes = len(app.minuteTrack)

    # replace minutes with above comment
    minutes = len(app.minuteTrack)
    xSpace = app.analytics_xSpan / minutes
    ySpace = app.analytics_ySpan / 10
    xStart, yStart = app.analytics_xStart, app.analytics_yStart
    xFreq,yFreq = minutes, 10
    drawGrid(canvas,xStart,yStart,xSpace,ySpace,xFreq,yFreq)

def drawGrid(canvas,xStart,yStart,xSpace,ySpace,xFreq,yFreq,color=None):
    for i in range(xFreq):
        for j in range(yFreq):
            x1, y1 = xStart+(i*xSpace), yStart+(j*ySpace)
            x2, y2 = x1 + xSpace, y1 + ySpace
            canvas.create_rectangle(x1,y1,x2,y2,fill=color)
            
            # draw x labels 
            if j == yFreq-1:
                canvas.create_text(x1,y2+ySpace/2,text=f'{i}',font='Helvetica 6 bold',
                        fill='black')
            # draw y labels from 0-10
            if i == 0:
                num = yFreq-j
                canvas.create_text(x1-xSpace/2,y1,text=f'{num}',font='Helvetica 6 bold',
                        fill='black')
                if j == yFreq-1:
                    canvas.create_text(x1-xSpace/2,y2, text='0',font='Helvetica 6 bold',
                            fill='black')

# draw green boxes indicating focus every 1/2 second
def analytics_teasePlot(app,canvas,time):
    minutes = len(app.minuteTrack)
    xSpace = app.analytics_xSpan / minutes
    ySpace = app.analytics_ySpan / -10
    xStart, yStart = app.analytics_xStart, app.analytics_yStart + app.analytics_ySpan
    xFreq,yFreq = minutes, 10
    time = int(time*2)
    if time > 10:
        time = 10
    drawDataGrid(app,canvas,xStart,yStart,xSpace,ySpace,xFreq,time,'#20E610')

def drawDataGrid(app,canvas,xStart,yStart,xSpace,ySpace,xFreq,yFreq,color):
    for i in range(xFreq):
        ratio = int(app.minuteTrack[str(i)] / (10*60) * 10)
        for j in range(yFreq):
            if j <= ratio:
                x1, y1 = xStart+(i*xSpace), yStart+(j*ySpace)
                x2, y2 = x1 + xSpace, y1 + ySpace
                canvas.create_rectangle(x1,y1,x2,y2,fill=color)

def analytics_keyPressed(app, event):
    if event.key == 'n':
        app.viewingSession -= 1
        if not app.viewingSession >= 0:
            app.viewingSession += 1
        else:
            loadSession(app)
    elif event.key == 'Escape':
        init_home(app)
        app.mode = 'home'
        

def analytics_timerFired(app):
    if not app.drawn:
        app.drawn = True
    app.e = time.time()
    app.elapsed = app.e - app.s

def stringToPixel(string):
    return len(string) *  16

def analytics_redrawAll(app,canvas):
    if not app.drawn:
        clear(canvas)

    analytics_drawPlot(app,canvas)
    if app.elapsed != None:
        analytics_teasePlot(app,canvas,app.elapsed)

    ##############################  
    # analytics display
    ##############################
    font,color = 'Helvetica 12 bold','black'
    cx,cy = app.analytics_nameCx, app.analytics_nameCy
    w,h = app.analytics_nameWidth, app.analytics_nameHeight
    w = stringToPixel(app.viewingSessionName)/2 
    canvas.create_rectangle(cx-w,cy-h,cx+w,cy+h)
    canvas.create_text(cx,cy,text=app.viewingSessionName,font=font,fill=color)
    
    cx,cy = app.analytics_timeCx, app.analytics_timeCy
    w,h = app.analytics_timeWidth, app.analytics_timeHeight
    w = stringToPixel(app.viewingSessionTime)/2 
    canvas.create_rectangle(cx-w,cy-h,cx+w,cy+h)
    canvas.create_text(cx,cy,text=app.viewingSessionTime,font=font,fill=color)

    cx,cy = app.analytics_descCx, app.analytics_descCy
    w,h, = app.analytics_descWidth, app.analytics_descHeight
    w = stringToPixel(app.viewingSessionDesc)/2
    canvas.create_rectangle(cx-w,cy-h,cx+w,cy+h)
    canvas.create_text(cx,cy,text=app.viewingSessionDesc,font=font,fill=color)
    # useful to have a function that draws data graphically (later)

    canvas.create_text(100, 100, text='press n to get next session', font='Hevetica 12 bold', 
            fill='black')

runApp(width=1280, height=720)


