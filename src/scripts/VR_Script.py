# Vr Template V2.1
#
# Author: Opheroth
#
# Update Date (YYYY/MM/DD): 2024/08/10

# Special thanks to VIP patrons:
#--------------------------------------------
#                  潇静 章                  #
#                Yung Satchi                #
#                 Magnus Roe                #
#--------------------------------------------

import threading
import bge, bpy, mathutils, math, bl_math, datetime
from mathutils import Vector
from collections import OrderedDict
import faulthandler

faulthandler.enable()

#To access global variables stored in bge.logic and make it
#easier to read in code.
globVar = bge.logic

scene = bge.logic.getCurrentScene()
cont = bge.logic.getCurrentController()
own = cont.owner

VR_Position = scene.objects["VR_Position"]
VR_Position_Empty = scene.objects["VR_Position_Empty"]
VR_Viewer_Empty = scene.objects["VR_Viewer_Empty"]
feet = scene.objects["Feet"]
leftHand = scene.objects["LeftTouch"]
leftFist = scene.objects['LeftFistCollision']
leftFinger = scene.objects['LeftFingerCollision']
leftPointer = scene.objects['LeftPointerEmpty']
leftHandVisual = scene.objects["LeftTouchVisual"]
rightHand = scene.objects["RightTouch"]
rightFist = scene.objects['RightFistCollision']
rightFinger = scene.objects['RightFingerCollision']
rightPointer = scene.objects['RightPointerEmpty']
rightHandVisual = scene.objects["RightTouchVisual"]
VR_Camera = scene.objects["VR_Camera"]
pointerNullL = scene.objects["PointerNullL"]
pointerNullR = scene.objects["PointerNullR"]
camFade = scene.objects["cameraFade"]
camFade2 = scene.objects["cameraFade2"]
climbRayCast = scene.objects["ClimbRayCast"]
hitPos = scene.objects["HitPos"]
hitPosPin = scene.objects["HitPosPin"]
laserToPointer = scene.objects["LaserToPointer"]
laser = scene.objects['LaserToPointer']
menu = scene.objects["MenuEmpty"]
rightMenuPointer = scene.objects["RightMenuPointer"]
leftMenuPointer = scene.objects["LeftMenuPointer"]
menuSelectCursor = scene.objectsInactive['MenuSelectCursor']
rightLineMenu = scene.objects['RightLineMenu']
leftLineMenu = scene.objects['LeftLineMenu']

tracking = laserToPointer.actuators["Tracking"]
#cont.activate(tracking)
leftRay = cont.sensors["LeftTouchRay"]
rightRay = cont.sensors["RightTouchRay"]

xr = bpy.context.window_manager.xr_session_state
xrs = bpy.context.window_manager.xr_session_settings
    
gripLocL = xr.controller_grip_location_get(bpy.context,0)
gripLocR = xr.controller_grip_location_get(bpy.context,1)
viewerPos = xr.viewer_pose_location

gripRotL = xr.controller_grip_rotation_get(bpy.context,0)
gripRotR = xr.controller_grip_rotation_get(bpy.context,1)
viewerRot = xr.viewer_pose_rotation

aimRot1 = xr.controller_aim_rotation_get(bpy.context,0)
aimRot2 = xr.controller_aim_rotation_get(bpy.context,1)

#Calculate delta time
def deltaTime():
    #return (datetime.datetime.now() - bge.logic.time).microseconds
    return (VR_Position["Timer"] - VR_Position["deltaTime"])

#--------Callback for copy Location and Rotation---------
def copyTransforms():
    #Motion Compensation fix for hands
    MComp = VR_Position['navLocation'] - xr.navigation_location
    
    #Rotation around Z axis using Euler
    RZE = mathutils.Vector([0,0,0])
    RZE[2] = (xr.navigation_rotation.to_euler()[2] - VR_Position['navRotation'].to_euler()[2])
    RZ = RZE[2]
    
    #if globVar.climbLeft == False and globVar.climbRight == False:
    #Copy Navigation Location and Rotation
    if VR_Position['copyNavLoc'] == True:
        own['copyNavLoc'] = False
        xr.navigation_location = VR_Position['navLocation']
        VR_Position.worldPosition = VR_Position['navLocation']
    if VR_Position['copyNavRot'] == True:
        own['copyNavRot'] = False
        xr.navigation_rotation = VR_Position['navRotation']
            
    #Copy VR Cam Location and Rotation    
    if VR_Position['copyVRCamPos'] == True:
        VR_Position['copyVRCamPos'] = False
        RVect = xr.viewer_pose_location - xr.navigation_location
        getCompV = rotComp(RVect, RZ, xr.navigation_location, VR_Position['VRCamPos'])
        VR_Camera.worldPosition = MComp + getCompV #VR_Position['VRCamPos']
    if VR_Position['copyVRCamRot'] == True:
        VR_Position['copyVRCamRot'] = False        
        VR_Camera.orientation = VR_Position['VRCamRot']
        VR_Camera.applyRotation([0,0,-RZ],False)

    #Copy Feet Location and Rotation
    if VR_Position['copyFeetLoc'] == True:
        VR_Position['copyFeetLoc'] = False
        feet.worldPosition = own['feetLocation']
    if VR_Position['copyFeetRot'] == True:
        own['copyFeetRot'] = False
        feet.orientation = own['feetRotation']
    #FeetLocationXY
    if VR_Position['copyFeetLocXY'] == True:
        VR_Position['copyFeetLocXY'] = False
        feet.worldPosition[0] = own['feetLocationXY'][0]
        feet.worldPosition[1] = own['feetLocationXY'][1]
    
      
    #Copy Right Hand Location and Rotation
    if VR_Position['copyRHandLoc'] == True:
        VR_Position['copyRHandLoc'] = False
        RVect = xr.controller_grip_location_get(bpy.context,1) - VR_Position['VRCamPos']
        getCompV = rotComp(RVect, RZ, VR_Position['VRCamPos'], own['rHandLocation'])
        rightHand.worldPosition = getCompV + MComp
    if VR_Position['copyRHandRot'] == True:
        VR_Position['copyRHandRot'] = False
        rightHand.orientation = mathutils.Quaternion(own['rHandRotation'])
        rightHand.applyRotation([0,0,-RZ],False)
        

    #Copy Left Hand Location and Rotation
    if VR_Position['copyLHandLoc'] == True:
        VR_Position['copyLHandLoc'] = False
        RVect = xr.controller_grip_location_get(bpy.context,0) - VR_Position['VRCamPos']
        getCompV = rotComp(RVect, RZ, VR_Position['VRCamPos'], own['lHandLocation'])
        leftHand.worldPosition = getCompV + MComp
    if VR_Position['copyLHandRot'] == True:
        VR_Position['copyLHandRot'] = False
        leftHand.orientation = mathutils.Quaternion(own['lHandRotation'])
        leftHand.applyRotation([0,0,-RZ],False)

     #Copy Right Hand Visual Location and Rotation
    if VR_Position['copyRHandVLoc'] == True:
        VR_Position['copyRHandVLoc'] = False
        RVect = xr.controller_grip_location_get(bpy.context,1) - VR_Position['VRCamPos']
        getCompV = rotComp(RVect, RZ, VR_Position['VRCamPos'], own['rHandVisualLocation'])
        rightHandVisual.worldPosition = getCompV + MComp
    if VR_Position['copyRHandVRot'] == True:
        VR_Position['copyRHandVRot'] = False
        rightHandVisual.orientation = mathutils.Quaternion(own['rHandVisualRotation'])
        rightHandVisual.applyRotation([0,0,-RZ],False)

    #Copy Left Hand Visual Location and Rotation
    if VR_Position['copyLHandVLoc'] == True:
        VR_Position['copyLHandVLoc'] = False
        RVect = xr.controller_grip_location_get(bpy.context,0) - VR_Position['VRCamPos']
        getCompV = rotComp(RVect, RZ, VR_Position['VRCamPos'], own['lHandVisualLocation'])
        leftHandVisual.worldPosition = getCompV + MComp
    if VR_Position['copyLHandVRot'] == True:
        VR_Position['copyLHandVRot'] = False
        leftHandVisual.orientation = mathutils.Quaternion(own['lHandVisualRotation'])
        leftHandVisual.applyRotation([0,0,-RZ],False)

#Rotation Compensation
#Vector from actual reading, angle to rotate, 
#vector from actual origin, vector to apply the compensation
def rotComp(_RCVect, _Angle, vectOrigin, vectEnd):
    xComp = _RCVect[0] * math.cos(_Angle) + _RCVect[1] * math.sin(_Angle)
    yComp = -_RCVect[0] * math.sin(_Angle) + _RCVect[1] * math.cos(_Angle)
    #Rotation Compensation
    RComp = mathutils.Vector([0,0,0])
    RComp[0] = vectOrigin[0] + xComp
    RComp[1] = vectOrigin[1] + yComp
    RComp[2] = vectEnd[2]
    return RComp

#Copy Navigation Location and Rotation on callback
def navLocCB(_NLCB):
    VR_Position['navLocation'] = _NLCB
    VR_Position['copyNavLoc'] = True
def navRotCB(_NRCB):
    VR_Position['navRotation'] = _NRCB
    VR_Position['copyNavRot'] = True
    
    
#Copy Feet Location and Rotation on callback
def feetLocCB(_FLCB):
    VR_Position['feetLocation'] = _FLCB
    VR_Position['copyFeetLoc'] = True
def feetRotCB(_FRCB):
    VR_Position['feetRotation'] = _FRCB
    VR_Position['copyFeetRot'] = True

def feetLocCBXY(_FLCBXY):
    VR_Position['feetLocationXY'] = _FLCBXY
    VR_Position['copyFeetLocXY'] = True
    
#Copy VRCam Location and Rotation on callback
def VRCamLocCB(_VRCLCB):
    VR_Position['VRCamPos'] = _VRCLCB
    VR_Position['copyVRCamPos'] = True
def VRCamRotCB(_VRCRCB):
    VR_Position['VRCamRot'] = _VRCRCB
    VR_Position['copyVRCamRot'] = True

#Copy Right Hand Visual Position and Rotation
def rHandVLocCB(_RHVLCB):
    VR_Position['rHandVisualLocation'] = _RHVLCB
    VR_Position['copyRHandVLoc'] = True
def rHandVRotCB(_RHVRCB):
    VR_Position['rHandVisualRotation'] = _RHVRCB
    VR_Position['copyRHandVRot'] = True        

#Copy Left Hand Visual Position and Rotation
def lHandVLocCB(_LHVLCB):
    VR_Position['lHandVisualLocation'] = _LHVLCB
    VR_Position['copyLHandVLoc'] = True
def lHandVRotCB(_LHVRCB):
    VR_Position['lHandVisualRotation'] = _LHVRCB
    VR_Position['copyLHandVRot'] = True        

#Copy Right Hand Position and Rotation
def rHandLocCB(_RHLCB):
    VR_Position['rHandLocation'] = _RHLCB
    VR_Position['copyRHandLoc'] = True
def rHandRotCB(_RHRCB):
    VR_Position['rHandRotation'] = _RHRCB
    VR_Position['copyRHandRot'] = True        

#Copy Left Hand Visual Position and Rotation
def lHandLocCB(_LHLCB):
    VR_Position['lHandLocation'] = _LHLCB
    VR_Position['copyLHandLoc'] = True
def lHandRotCB(_LHRCB):
    VR_Position['lHandRotation'] = _LHRCB
    VR_Position['copyLHandRot'] = True   

#----------------Vibration-------------------------------
def vibration(_hand, _time, _freq, _amp):
        if _freq == "high":
            _freq2 = 300
        elif _freq == "low":
            _freq2 = 160
        if _hand == "left":
            _hand2 = "/user/hand/left"
        elif _hand == "right":
            _hand2 = "/user/hand/right"
        xr.haptic_action_apply(bpy.context,"blender_generic", "haptic", _hand2,_time*1000000, _freq2, _amp)
#--------------------Hide Teleport Pin------------------
def hideTeleportPin():
    hitPos.visible = False
    hitPosPin.visible = False
    laserToPointer.visible = False

#-------------------Show Teleport Pin-------------------
def showTeleportPin():
    hitPos.visible = True
    hitPosPin.visible = True
    laserToPointer.visible = True

#----------------Teleport-------------------------------
def teleport(_Position, _teleportSide):
    if globVar.pointingL == 1 or globVar.pointingR == 1:
        globVar.tempPos = _Position
        fade(_teleportSide)
        globVar.teleportingL = True
        globVar.teleportingR = True
        offset = viewerPos - xr.navigation_location
        xr.navigation_location[0] = _Position[0] - offset[0]
        xr.navigation_location[1] = _Position[1] - offset[1]
        xr.navigation_location[2] = _Position[2] -0.025
        feet.worldPosition[0] = _Position[0]
        feet.worldPosition[1] = _Position[1]
        feet.worldPosition[2] = _Position[2] + 0.13
        globVar.climbLeft = False
        globVar.climbRight = False
        #xrs.clip_end = scene.objects['_Config']['ClipEnd']

def dash(_Position, _speed):
    bge.logic.dashSpeed = _speed
    globVar.tempPos = _Position
    bge.logic.dashing = True
    offset = viewerPos - xr.navigation_location
    bge.logic.dash = mathutils.Vector([_Position[0] - offset[0], _Position[1] - offset[1], _Position[2]+0.075])
    
    if (_Position[2] - feet.worldPosition[2]) > 0.1:
        bge.logic.dashFeet = mathutils.Vector([_Position[0] - offset[0], _Position[1] - offset[1], _Position[2] + 0.13])
    else:
        bge.logic.dashFeet = mathutils.Vector([_Position[0] - offset[0], _Position[1] - offset[1], _Position[2] + 0.075])

#------Fade--------
def fade(_fadeSide):
    camFade["Fade"] = True
    camFade2['Fade'] = True
    print("Fading", end='')
    while camFade["FadeFrame"] < 8:
        print("", end='') #For some reason, not printing on console at this point, decreases performance drastically    
        VR_Camera.worldPosition = xr.viewer_pose_location
        VR_Camera.orientation = xr.viewer_pose_rotation
    while camFade["FadeFrame"] > 8 and camFade["FadeFrame"] < 10:
        xrs.clip_end = 0.11
        print('',end='') #For some reason, not printing on console at this point, decreases performance drastically    
        VR_Camera.worldPosition = xr.viewer_pose_location
        VR_Camera.orientation = xr.viewer_pose_rotation
        camFade2.orientation = xr.viewer_pose_rotation
        
        if _fadeSide == "left":    
            camFade2.worldPosition[0] = globVar.LRHitPos[0]
            camFade2.worldPosition[1] = globVar.LRHitPos[1]
            camFade2.worldPosition[2] = globVar.LRHitPos[2] + VR_Camera.worldPosition[2] - feet.worldPosition[2]+0.13

        if _fadeSide == "right":    
            camFade2.worldPosition[0] = hitPos.worldPosition[0]
            camFade2.worldPosition[1] = hitPos.worldPosition[1]
            camFade2.worldPosition[2] = globVar.RRHitPos[2] + VR_Camera.worldPosition[2]  - feet.worldPosition[2]+0.13
    
    xrs.clip_end = scene.objects['_Config']['ClipEnd']
    camFade["Fade"] = False
    camFade2['Fade'] = False

def VR_Init():
    #Initialize variables to avoid errors while
    #trying to read them before assigning values
    if VR_Position["Init"] == True:
        VR_Position["Init"] = False
        
        leftRay.range = scene.objects["_Config"]["TeleportMaxDistance"]
        rightRay.range = scene.objects["_Config"]["TeleportMaxDistance"]
        VR_Position["deltaTime"] = VR_Position["Timer"]
        globVar.Fading = True
        globVar.climbLeft = False
        globVar.climbRight = False
        globVar.climbing = False
        globVar.resetLoc = [0,0,0]
        globVar.pointingL = 0
        globVar.pointingR = 0
        globVar.LRHitPos = [0,0,0]
        globVar.RRHitPos = [0,0,0]
        globVar.rotatingL = 0
        globVar.rotatingR = 0
        globVar.teleportingL = False
        globVar.teleportingR = False
        globVar.tempOrientation = VR_Position.orientation
        globVar.jumping = False
        globVar.vectorInertia = leftHand.getLinearVelocity()
        globVar.vector0 = globVar.vectorInertia
        globVar.vector1 = globVar.vectorInertia
        globVar.vector2 = globVar.vectorInertia
        globVar.vector3 = globVar.vectorInertia
        globVar.tempPos = hitPos.worldPosition
        LeftDist = [0,0,0] 
        bge.logic.openingDoor = False
        bge.logic.dash = [0,0,0]
        bge.logic.dashing = False
        posDashFeet = mathutils.Vector([0,0,0])
        
        
        # ----- Menu Buttons Section -----
        teleportButton = scene.objects["TeleportButton"]
        teleportButton.blenderObject["selectedAttr"] = 0.8
                
        teleportDashButton = scene.objects["TeleportDashButton"]
        teleportDashButton.blenderObject["selectedAttr"] = 0.8
                
        walkButton = scene.objects["WalkButton"]
        walkButton.blenderObject["selectedAttr"] = 0.8
        
        exitButton = scene.objects["ExitButton"]
        exitButton.blenderObject["selectedAttr"] = 0.8

        closeButton = scene.objects["CloseButton"]
        closeButton.blenderObject["selectedAttr"] = 0
        
        if scene.objects["_Config"]["Teleport"] == True:
            if scene.objects["_Config"]["Fade"] == True:
                teleportButton.blenderObject["selectedAttr"] = 0
            else:
                teleportDashButton.blenderObject["selectedAttr"] = 0
        else:
            walkButton.blenderObject["selectedAttr"] = 0
        
        
        teleportButton.blenderObject.update_tag()
        teleportDashButton.blenderObject.update_tag()
        walkButton.blenderObject.update_tag()
        exitButton.blenderObject.update_tag()
        closeButton.blenderObject.update_tag()
        
        #Set the custom Action Set I've configured            
        xr.active_action_set_set(bpy.context, "blender_generic")
        
        navRotCB(VR_Position.orientation.to_quaternion().copy())
        VR_Position_Empty.orientation = VR_Position.orientation
        VR_Camera.removeParent()
        bge.logic.dash = mathutils.Vector([0,0,0])
        
        globVar.pointingL = 1
        teleport([VR_Position.worldPosition[0], VR_Position.worldPosition[1], VR_Position.worldPosition[2]+0.3], 'Left')
        
        #dash((VR_Position.worldPosition[0],VR_Position.worldPosition[1],VR_Position.worldPosition[2]+0.25), 1)
        globVar.menuToggle = False
        globVar.menuHidden = True
        menu.worldPosition = [0,0,-100]
        
        if VR_Position["RuntimeInit"] == True:
            #bpy.context.scene.world = bpy.data.worlds[VR_Position["TempWorldName"]]
            VR_Position["RuntimeInit"] = False
        xrs.clip_end = scene.objects["_Config"]["ClipEnd"]

#Stop Camera going through indicated walls/objects
def stopCameraTresspasing():
    
    rejectMov = scene.objects["_Config"]["MotionSpeed"] *0.005
    #Camera stop at obstacles
    #                 to          from         dist
    #Empty.rayCast([X3, Y3, Z3], [X2, Y2, Z2], 5, "Ground")
    rayDist = 0.2
    VRCamPos = [0,0,0]
    VRCamPos[0] = VR_Camera.worldPosition[0]
    VRCamPos[1] = VR_Camera.worldPosition[1]
    VRCamPos[2] = VR_Camera.worldPosition[2]
    rayXNeg = [0,0,0]
    rayXNeg[0] = VRCamPos[0] - 1
    rayXNeg[1] = VRCamPos[1]
    rayXNeg[2] = VRCamPos[2]
    rayXPos = [0,0,0]
    rayXPos[0] = VRCamPos[0] + 1
    rayXPos[1] = VRCamPos[1]
    rayXPos[2] = VRCamPos[2]
    rayYNeg = [0,0,0]
    rayYNeg[0] = VRCamPos[0]
    rayYNeg[1] = VRCamPos[1] - 1
    rayYNeg[2] = VRCamPos[2]
    rayYPos = [0,0,0]
    rayYPos[0] = VRCamPos[0]
    rayYPos[1] = VRCamPos[1] + 1
    rayYPos[2] = VRCamPos[2]        
    loop = False
    
    rayTest = VR_Camera.rayCast(rayXNeg, VRCamPos, rayDist, "Obstacle", 0, 1)
    if str(rayTest[0]) != "None":
        dist = feet.worldPosition + mathutils.Vector([rejectMov, 0, 0])
        feetLocCBXY(dist)
        dist = xr.navigation_location + mathutils.Vector([rejectMov, 0, 0])
        navLocCB(mathutils.Vector([dist[0], dist[1], feet.worldPosition[2]]))
        dist = xr.viewer_pose_location + mathutils.Vector([rejectMov, 0, 0])
        VRCamLocCB(dist)

    rayTest = VR_Camera.rayCast(rayXPos, VRCamPos, rayDist, "Obstacle", 0, 1)
    if str(rayTest[0]) != "None":
        dist = feet.worldPosition - mathutils.Vector([rejectMov, 0, 0])
        feetLocCBXY(dist)
        dist = xr.navigation_location - mathutils.Vector([rejectMov, 0, 0])
        navLocCB(mathutils.Vector([dist[0], dist[1], feet.worldPosition[2]]))
        dist = xr.viewer_pose_location - mathutils.Vector([rejectMov, 0, 0])
        VRCamLocCB(dist)
    
    rayTest = VR_Camera.rayCast(rayYNeg, VRCamPos, rayDist, "Obstacle", 0, 1)
    if str(rayTest[0]) != "None":
        dist = feet.worldPosition + mathutils.Vector([0, rejectMov, 0])
        feetLocCBXY(dist)
        dist = xr.navigation_location + mathutils.Vector([0, rejectMov, 0])
        navLocCB(mathutils.Vector([dist[0], dist[1], feet.worldPosition[2]]))
        dist = xr.viewer_pose_location + mathutils.Vector([0, rejectMov, 0])
        VRCamLocCB(dist)
        

    rayTest = VR_Camera.rayCast(rayYPos, VRCamPos, rayDist, "Obstacle", 0, 1)
    if str(rayTest[0]) != "None":
        dist = feet.worldPosition - mathutils.Vector([0, rejectMov, 0])
        feetLocCBXY(dist)
        dist = xr.navigation_location - mathutils.Vector([0, rejectMov, 0])
        navLocCB(mathutils.Vector([dist[0], dist[1], feet.worldPosition[2]]))
        dist = xr.viewer_pose_location - mathutils.Vector([0, rejectMov, 0])
        VRCamLocCB(dist)
        
        
def handsInteraction():
    #Make the hands follow the VR controllers
    #And limit movent through obstacles
    if globVar.climbLeft == False:
        gLoc = xr.controller_grip_location_get(bpy.context,0)
        rayTest = VR_Camera.rayCast(gLoc, VR_Camera, VR_Camera.getDistanceTo(gLoc)+0.05, "Obstacle",0 ,1)
        if str(rayTest[0]) == "None" or bge.logic.openingDoor == True:
            setLeftHandLocRot()
        else:
            try:
                leftHandVisual.worldPosition = rayTest[1]
                lHandVRotCB(xr.controller_grip_rotation_get(bpy.context,0))
                leftHand.worldPosition = rayTest[1]
                lHandRotCB(xr.controller_grip_rotation_get(bpy.context,0))
            except:
                pass
                
            
    if globVar.climbRight == False:
        gLoc = xr.controller_grip_location_get(bpy.context,1)
        rayTest = VR_Camera.rayCast(gLoc, VR_Camera, VR_Camera.getDistanceTo(gLoc)+0.05, "Obstacle",0 ,1)
        if str(rayTest[0]) == "None" or bge.logic.openingDoor == True:
            setRightHandLocRot()
        else:
            try:
                rightHandVisual.worldPosition = rayTest[1]
                rHandVRotCB(xr.controller_grip_rotation_get(bpy.context,1))
                rightHand.worldPosition = rayTest[1]
                rHandRotCB(xr.controller_grip_rotation_get(bpy.context,1))
            except:
                pass
    
    #If both hands are not climbing, restore dynamics
    if globVar.climbLeft == False and globVar.climbRight == False:
        #setVRPos()
        feet.restoreDynamics()
        offset = xr.viewer_pose_location - xr.navigation_location
        navLocCB(mathutils.Vector([xr.navigation_location[0], xr.navigation_location[1], feet.worldPosition[2] ]))

 
 #Set Right Hand position and rotation
def setRightHandLocRot():
    rHandLocCB(xr.controller_grip_location_get(bpy.context,1))
    rHandRotCB(xr.controller_grip_rotation_get(bpy.context,1))
    
    if bge.logic.knob != 2:
        rHandVLocCB(xr.controller_grip_location_get(bpy.context,1))
        rHandVRotCB(xr.controller_grip_rotation_get(bpy.context,1))

#Set Left Hand position and rotation
def setLeftHandLocRot():
    lHandLocCB(xr.controller_grip_location_get(bpy.context,0))
    lHandRotCB(xr.controller_grip_rotation_get(bpy.context,0))

    if bge.logic.knob != 1:
        lHandVLocCB(xr.controller_grip_location_get(bpy.context,0))
        lHandVRotCB(xr.controller_grip_rotation_get(bpy.context,0))

def motionType():
    #If Locomotion is selected
    if scene.objects["_Config"]["Teleport"] == False:
        locomotionMovement()
        
    #If Teleport is selected
    if scene.objects["_Config"]["Teleport"] == True:
        teleportMovement()

#----------Locomotion Movement-------------------
def locomotionMovement():
    hideTeleportPin()
    #---------------------------------
    #Point and move
    #---------------------------------
    #Joystick Dead Zone
    deadZone = 0.15    

    #Movement Speed
    speed = scene.objects["_Config"]["MotionSpeed"]*deltaTime()*100
    movementAct = feet.actuators["ServoMotion"]
    
    moveX = 0
    moveY = 0
    moveZ = 0
    
    if globVar.leftStickX < -deadZone or globVar.leftStickX > deadZone or globVar.leftStickY < -deadZone or globVar.leftStickY > deadZone:
        globVar.menuHidden = True
        menu.worldPosition = [0,0,-100]
        #movementAct.linV = [globVar.leftStickX * speed, globVar.leftStickY * speed, feet.linearVelocity[2]]
        moveX = globVar.leftStickX * speed
        moveY = globVar.leftStickY * speed
        
        offset = viewerPos - xr.navigation_location
        offsetPos = mathutils.Vector([feet.worldPosition[0] - offset[0], feet.worldPosition[1] - offset[1], feet.worldPosition[2]])
        navLocCB(offsetPos)
        stopCameraTresspasing()
    else:
        feetLocCBXY([xr.viewer_pose_location[0], xr.viewer_pose_location[1], feet.worldPosition[2]])
        movementAct.linV[0] /= 200
        movementAct.linV[1] /= 200
        movementAct.linV[2] = feet.linearVelocity[2]
        movementAct.linV = [0,0,0]

    jumpingForce = 1.5
    if globVar.buttonA == 1:
        feet['JumpForce'] *= 0.9
        if feet["jumping"] == False and feet.sensors["CollisionNavmesh"].positive == True:
            globVar.menuHidden = True
            menu.worldPosition = [0,0,-100]
            feet["jumping"] = True
            feet['JumpForce'] = jumpingForce
        if feet['JumpForce'] > 0.1:
            #movementAct.linV = [feet.linearVelocity[0], feet.linearVelocity[1], feet['JumpForce'] * speed]
            moveZ = feet['JumpForce'] * speed
        else:
            moveZ = feet.linearVelocity[2]
    else:
        if feet['JumpForce'] < 0.1:
            moveZ = feet.linearVelocity[2]
        elif feet['JumpForce'] > 0.1:
            feet['JumpForce'] = 0
            moveZ = 0.01
        #movementAct.linV = [feet.linearVelocity[0], feet.linearVelocity[1], feet.linearVelocity[2]]
    if feet["jumping"] == True and feet.sensors["CollisionNavmesh"].positive == True and globVar.buttonA == 0:
        feet["jumping"] = False
    
    movementAct.linV = [moveX, moveY, moveZ]


    #---------------------------------
    #Rotate
    #---------------------------------
    rotateSpeed = scene.objects["_Config"]["RotationSpeed"]
    if globVar.rightStickX < -deadZone or globVar.rightStickX > deadZone:
        globVar.menuHidden = True
        menu.worldPosition = [0,0,-100]
        adjustRotationLocomotion(-globVar.rightStickX * rotateSpeed, "R")
        

#------------Adjust Rotation Locomotion-----------------
def adjustRotationLocomotion(_angle, _Hand):
    VR_Position_Empty.applyRotation([0,0,math.radians(_angle)],True)
    VR_Position.orientation = VR_Position_Empty.orientation
    navRotCB(VR_Position_Empty.orientation.to_quaternion())
        
#---Adjust the position to rotate around the Feet object
def adjustPositionCenter():
    navLocCB(mathutils.Vector([xr.navigation_location[0] - (viewerPos[0] - feet.worldPosition[0]), xr.navigation_location[1] - (viewerPos[1] - feet.worldPosition[1]), xr.navigation_location[2]]))

#----------Teleport Movement-------------------
def teleportMovement():
    #---------------------------------
    #Point and move
    #---------------------------------
    #Check the left controller Stick
    globVar.LRHitPos = leftRay.hitPosition
    if globVar.leftStickY > 0.7:
        globVar.menuHidden = True
        menu.worldPosition = [0,0,-100]
        leftPointing()
    else:
        tryToTeleportL()

    #Check the right controller Stick
    if globVar.rightStickY > 0.7:
        globVar.menuHidden = True
        menu.worldPosition = [0,0,-100]
        rightPointing()
    else:
        tryToTeleportR()
        
    #Hide teleport pin when not in use
    if globVar.pointingR == 0 and globVar.pointingL == 0: 
        hitPos.worldPosition = [0,0,-100]
        hideTeleportPin()
    
    
    #if Dash movement is selected
    if scene.objects["_Config"]["Dash"] == True:
        if bge.logic.climbRight == False and bge.logic.climbLeft == False:
            dashSpeed = bge.logic.dashSpeed
                
            marg = 0.001
            if globVar.dashing == True:
                posDashFeet = mathutils.Vector.lerp(feet.worldPosition, mathutils.Vector([bge.logic.dashFeet[0], bge.logic.dashFeet[1], bge.logic.dashFeet[2]]), dashSpeed)
    
                offset = viewerPos - xr.navigation_location
                offset[2] = feet.worldPosition[2] - 0.12
                #posDash = feet.worldPosition - offset
                
                posDash = mathutils.Vector.lerp(xr.navigation_location, mathutils.Vector([bge.logic.dash[0], bge.logic.dash[1], bge.logic.dash[2]]), dashSpeed)
              
                feet.suspendPhysics()
                feetLocCB(posDashFeet)
                navLocCB(posDash)
            else:
                feetLocCBXY([xr.viewer_pose_location[0], xr.viewer_pose_location[1], feet.worldPosition[2]])

            if abs(xr.navigation_location[0] - bge.logic.dash[0]) < marg:
                if abs(xr.navigation_location[1] - bge.logic.dash[1]) < marg:
                    if VR_Position["Timer"] > 2:
                        feet.restorePhysics()
                    globVar.dashing = False

 
    else:
        pass
        feetLocCBXY([xr.viewer_pose_location[0], xr.viewer_pose_location[1], feet.worldPosition[2]])
    #---------------------------------
    #Rotate
    #---------------------------------
    rotateLStick()
    rotateRStick()  

#-----------------------------------------------------------------------
#   LEFT HAND        
#----------------Left Pointing--------------------------
def tryToTeleportL():
    pointerNullL.worldPosition = [0,0,-100]
    if leftRay.positive and globVar.teleportingL == False and globVar.pointingL == 1:
        if scene.objects["_Config"]["Dash"] == True:
            dash(globVar.LRHitPos, 0.5)
        else:
            teleport(globVar.LRHitPos, "left")
    globVar.pointingL = 0
    
def leftPointing():
    globVar.teleportingL = False
    if leftRay.hitPosition == [0,0,0]:
        pointerNullL.visible = True
        pointerNullL.worldPosition = xr.controller_grip_location_get(bpy.context,0)
        pointerNullL.orientation = xr.controller_grip_rotation_get(bpy.context,0)
        globVar.pointingL = 0
    else:
        showTeleportPin()
        pointerNullL.worldPosition = [0,0,-100]
        if leftRay.positive and globVar.pointingR == 0:
            globVar.pointingL = 1
            globVar.LRHitPos = leftRay.hitPosition
            hitPos.worldPosition = leftRay.hitPosition
            hitPos.alignAxisToVect(Vector(leftRay.hitNormal),2,1)
            tracking.object = scene.objects["LeftTouch"]
            laser.localScale = [1,1, laser.getDistanceTo(scene.objects["LeftTouch"])]
        
#----------------Rotate Left Stick----------------------
def rotateLStick():
    if globVar.leftStickX > 0.8 and globVar.rotatingL == 0:
        adjustRotation(-45, "L")

    elif globVar.leftStickX < -0.8 and globVar.rotatingL == 0:
        adjustRotation(45, "L")
 
    elif globVar.leftStickY < -0.7 and globVar.rotatingL == 0:
        adjustRotation(-180, "L")

    elif globVar.leftStickX < 0.1 and globVar.leftStickX > -0.1:
        if globVar.leftStickY < 0.1 and globVar.leftStickY > -0.1:
            globVar.rotatingL = 0

#-----------------------------------------------------------------------
#   RIGHT HAND        
#----------------Right Pointing--------------------------
def tryToTeleportR():
    pointerNullR.worldPosition = [0,0,-100]
    if rightRay.positive and globVar.teleportingR == False and globVar.pointingR == 1:
        if scene.objects["_Config"]["Dash"] == True:
            dash(globVar.RRHitPos, 0.5)
        else:
            teleport(globVar.RRHitPos, "right")
    globVar.pointingR = 0

def rightPointing():
    globVar.teleportingR = False
    if rightRay.hitPosition == [0,0,0]:
        pointerNullR.visible = True
        pointerNullR.worldPosition = xr.controller_grip_location_get(bpy.context,1)
        pointerNullR.orientation = xr.controller_grip_rotation_get(bpy.context,1)
        globVar.pointingR = 0
    else:
        showTeleportPin()
        pointerNullR.worldPosition = [0,0,-100]
    if rightRay.positive and globVar.pointingL == 0:
        globVar.pointingR = 1
        globVar.RRHitPos = rightRay.hitPosition
        hitPos.worldPosition = rightRay.hitPosition
        hitPos.alignAxisToVect(Vector(rightRay.hitNormal),2,1)
        tracking.object = scene.objects["RightTouch"]
        laser.localScale = [1,1, laser.getDistanceTo(scene.objects["RightTouch"])]
        
#----------------Rotate Right Stick----------------------
def rotateRStick():
    if globVar.rightStickX > 0.8 and globVar.rotatingR == 0:
        adjustRotation(-45, "R")

    elif globVar.rightStickX < -0.8 and globVar.rotatingR == 0:
        adjustRotation(45, "R")
 
    elif globVar.rightStickY < -0.7 and globVar.rotatingR == 0:
        adjustRotation(-180, "R")

    elif globVar.rightStickX < 0.1 and globVar.rightStickX > -0.1:
        if globVar.rightStickY < 0.1 and globVar.rightStickY > -0.1:
            globVar.rotatingR = 0

#------------Adjust Rotation----------------------------    
def adjustRotation(_angle, _Hand):
    if _Hand == "L":
        globVar.rotatingL = 1
    else:
        globVar.rotatingR = 1
        
    VR_Position_Empty.applyRotation([0,0,math.radians(_angle)],True)
    VR_Position.orientation = VR_Position_Empty.orientation
    navRotCB(VR_Position_Empty.orientation.to_quaternion())
    
#-----Set the VR_Position object under viewer's head-------
def setVRPos():
    VR_Position.worldPosition[0] = viewerPos[0]
    VR_Position.worldPosition[1] = viewerPos[1]

#-------------------------LEFT HAND GRAB---------------------------------
#Grab objects with left hand    
def handGrabLeft():
    #If hand collides with object, check if we try to grab it
    if len(leftHand.sensors["LeftTouchCollision"].hitObjectList) > 0:
        climbGrabUse()
        
    if globVar.leftGrip > 0.9:
        leftHand["Closed"] = True
    if globVar.leftGrip < 0.1:
        leftHand["Closed"] = False
        leftHand["Grabbing"] = False
        globVar.climbLeft = False
        if len(leftHand.children) > 0:
            Inertia = leftHand.children[0].getLinearVelocity()
            AngVel = leftHand.children[0].getAngularVelocity()
            tempname = leftHand.children[0]
            leftHand.children[0].removeParent() 
            bge.logic.leftObjMass = tempname.mass 
            if bge.logic.leftObjMass == 0:
                bge.logic.leftObjMass = 1
            scene.objects[str(tempname)].setLinearVelocity(Inertia * 1.2 / globVar.leftObjMass)
            scene.objects[str(tempname)].setAngularVelocity(AngVel / globVar.leftObjMass)
            globVar.climbLeft = False


#Defines if we grab/use an object or are climbing    
def climbGrabUse():
    LeftGrabObj = leftHand.sensors["LeftTouchCollision"].hitObjectList[0]
    if globVar.leftGrip > 0.7 and leftHand["Closed"] == False and leftHand["Grabbing"] == False:
        globVar.leftObjMass = LeftGrabObj.mass
        if "Climb" in LeftGrabObj.getPropertyNames():
            if globVar.climbLeft == False:
                vibration("left", 0.01, "high", 0.5)
                bge.logic.climbLeft = True
                feet.suspendDynamics()
                globVar.lTempFeetPos = feet.worldPosition
                globVar.xrNavTempPos = xr.navigation_location
        else:
            if "Use" in LeftGrabObj.getPropertyNames():
                LeftGrabObj.removeParent()
                LeftGrabObj.worldPosition = xr.controller_grip_location_get(bpy.context,0)
                LeftGrabObj.orientation = xr.controller_grip_rotation_get(bpy.context,0)
                LeftGrabObj.setParent(leftHand, False, False)
                vibration("left", 0.01, "high", 0.5)
                LeftGrabObj["Grab"] = True
                leftHand["Grabbing"] = True
            else:
                LeftGrabObj.setParent(leftHand, False, False)
                vibration("left", 0.01, "high", 0.5)
                leftHand["Grabbing"] = True
                
#-------------------------RIGHT HAND GRAB---------------------------------
#Grab objects with right hand    
def handGrabRight():
    #If hand collides with object, check if we try to grab it
    if len(rightHand.sensors["RightTouchCollision"].hitObjectList) > 0:
        climbGrabUseR()
    
    if globVar.rightGrip > 0.9:
        rightHand["Closed"] = True
    if globVar.rightGrip < 0.1:
        rightHand["Closed"] = False
        rightHand["Grabbing"] = False
        globVar.climbRight = False
        if len(rightHand.children) > 0:
            #Inertia = rightHand.getLinearVelocity()
            Inertia = rightHand.children[0].getLinearVelocity()
            AngVel = rightHand.children[0].getAngularVelocity()
            tempname = rightHand.children[0]
            #rightFist.suspendPhysics()
            rightHand.children[0].removeParent() 
            bge.logic.rightObjMass = tempname.mass 
            if bge.logic.rightObjMass == 0:
                bge.logic.rightObjMass = 1 
            scene.objects[str(tempname)].setLinearVelocity(Inertia * 1.2 / globVar.rightObjMass)
            scene.objects[str(tempname)].setAngularVelocity(AngVel / globVar.rightObjMass)

#Defines if we grab/use an object or are climbing    
def climbGrabUseR():
    rightGrabObj = rightHand.sensors["RightTouchCollision"].hitObjectList[0]
    if globVar.rightGrip > 0.7 and rightHand["Closed"] == False and rightHand["Grabbing"] == False:
        globVar.rightObjMass = rightGrabObj.mass
        if "Climb" in rightGrabObj.getPropertyNames():
            if globVar.climbRight == False:
                vibration("right", 0.01, "high", 0.5)
                bge.logic.climbRight = True
                feet.suspendDynamics()
                globVar.xrNavTempPos = xr.navigation_location
                globVar.rTempFeetPos = feet.worldPosition
        else:
            if "Use" in rightGrabObj.getPropertyNames():
                rightGrabObj.removeParent()
                rightGrabObj.worldPosition = rightHand.worldPosition
                rightGrabObj.orientation = rightHand.orientation
                #bpy.data.objects[rightGrabObj.name].game.use_collision_compound = True
                #rightGrabObj.setParent(rightFist, True)
                rightGrabObj.setParent(rightHand, True, False)
                vibration("right", 0.01, "high", 0.5)
                rightGrabObj["Grab"] = True
                rightHand["Grabbing"] = True
            else:
                #bpy.data.objects[rightGrabObj.name].game.use_collision_compound = True
                rightGrabObj.setParent(rightHand, True, False)
                #rightGrabObj.setParent(rightFist)
                vibration("right", 0.01, "high", 0.5)
                rightHand["Grabbing"] = True

def climbing():
    if globVar.climbLeft == True and globVar.climbRight == False:
        leftDist = (leftHand.worldPosition - xr.controller_grip_location_get(bpy.context,0))/2
        navLocCB(globVar.xrNavTempPos + leftDist)
        feet.worldPosition = globVar.lTempFeetPos + leftDist
        bge.logic.dash = xr.navigation_location
    
    if globVar.climbLeft == False and globVar.climbRight == True:
        rightDist = (rightHand.worldPosition - xr.controller_grip_location_get(bpy.context,1))/2
        navLocCB(globVar.xrNavTempPos + rightDist)
        feet.worldPosition = globVar.rTempFeetPos + rightDist
        bge.logic.dash = xr.navigation_location

    if globVar.climbLeft == True and globVar.climbRight == True:
        leftDist = (leftHand.worldPosition - xr.controller_grip_location_get(bpy.context,0))/2
        rightDist = (rightHand.worldPosition - xr.controller_grip_location_get(bpy.context,1))/2
        navLocCB(((globVar.xrNavTempPos + globVar.xrNavTempPos) / 2) + ((rightDist + leftDist) / 2))
        feet.worldPosition = ((globVar.lTempFeetPos + globVar.lTempFeetPos) / 2) + ((leftDist + rightDist) / 2)
        bge.logic.dash = xr.navigation_location
            

def isMenuActivated():
    
    if globVar.buttonB == 1 or globVar.buttonY == 1:
        if bge.logic.menuToggle == False:
            bge.logic.menuToggle = True
            if bge.logic.menuHidden == True:
                scene.objects["MenuEmpty"].orientation = mathutils.Quaternion([xr.viewer_pose_rotation[0], 0, 0, xr.viewer_pose_rotation[3]])
                bge.logic.menuHidden = False
            else:
                bge.logic.menuHidden = True
                menu.worldPosition = [0,0,-100]
    else:
        bge.logic.menuToggle = False

    if bge.logic.menuHidden == False:
        viewDif = abs(scene.objects["MenuEmpty"].orientation.to_euler()[2] - scene.objects["VR_Camera"].orientation.to_euler()[2])
        if viewDif > 0.5:
            scene.objects["MenuEmpty"].orientation = mathutils.Quaternion([xr.viewer_pose_rotation[0], 0, 0, xr.viewer_pose_rotation[3]])        
        menu.worldPosition += (viewerPos - menu.worldPosition)/2

def isMenuRay():
    #---------------Right Hand----------------------------------------
    rightRayMenu = rightFist.rayCast(rightPointer.worldPosition, rightFinger.worldPosition, 5, 'Menu', 0, True, 0)
    if str(rightRayMenu[0]) != 'None':
        rHitPoint = rightRayMenu[1]
        rightMenuPointer.visible = True
        rightLineMenu.visible = True
        smoothRPoint = (rHitPoint + rightMenuPointer['Pos_1'] + rightMenuPointer['Pos_2'] + rightMenuPointer['Pos_3']) /4 # + rightMenuPointer['Pos_4'] + rightMenuPointer['Pos_5'] + rightMenuPointer['Pos_6']) / 7
        rightMenuPointer.worldPosition = smoothRPoint
        rightMenuPointer.alignAxisToVect(rightRayMenu[2])
        rDist = VR_Camera.getDistanceTo(rHitPoint)
        rScale = rDist * 1.3
        
        rTrackDist = rightLineMenu.getDistanceTo(rightMenuPointer) * 0.8
        rightLineMenu.localScale = [rTrackDist*.8,rTrackDist,rTrackDist*.8]
        rTrack = rightLineMenu.getVectTo(rightMenuPointer)
        rightLineMenu.alignAxisToVect(rTrack[1], 1, 1.0)
        rightLineMenu.worldPosition = rightPointer.worldPosition
        
        if rScale > 5:
            rScale = 5
        if globVar.rightTrigger > 0.5:
            rScale *= 1.15
            if rightMenuPointer['Pressed'] == False:
                rightMenuPointer['Pressed'] = True
                vibration("right", 0.02, "high", 0.5)
                scene.addObject(menuSelectCursor, rightMenuPointer, 1.5,False)
        else:
            rightMenuPointer['Pressed'] = False
        
        rightMenuPointer.localScale = [rScale, rScale, rScale]
        rightMenuPointer['Pos_3'] = rightMenuPointer['Pos_2']
        rightMenuPointer['Pos_2'] = rightMenuPointer['Pos_1']
        rightMenuPointer['Pos_1'] = rHitPoint.copy()
    else:
        rightMenuPointer.visible = False
        rightLineMenu.visible = False
    
    #---------------Left Hand----------------------------------------
    leftRayMenu = leftFist.rayCast(leftPointer.worldPosition, leftFinger.worldPosition, 5, 'Menu', 0, True, 0)
    if str(leftRayMenu[0]) != 'None':
        lHitPoint = leftRayMenu[1]
        leftMenuPointer.visible = True
        leftLineMenu.visible = True
        smoothLPoint = (lHitPoint + leftMenuPointer['Pos_1'] + leftMenuPointer['Pos_2'] + leftMenuPointer['Pos_3']) /4 # + leftMenuPointer['Pos_4'] + leftMenuPointer['Pos_5'] + leftMenuPointer['Pos_6']) / 7
        leftMenuPointer.worldPosition = smoothLPoint
        leftMenuPointer.alignAxisToVect(leftRayMenu[2])
        lDist = VR_Camera.getDistanceTo(lHitPoint)
        lScale = lDist * 1.3
        
        lTrackDist = leftLineMenu.getDistanceTo(leftMenuPointer) * 0.8
        leftLineMenu.localScale = [lTrackDist*.8,lTrackDist,lTrackDist*.8]
        lTrack = leftLineMenu.getVectTo(leftMenuPointer)
        leftLineMenu.alignAxisToVect(lTrack[1], 1, 1.0)
        leftLineMenu.worldPosition = leftPointer.worldPosition
        
        if lScale > 5:
            lScale = 5
        if globVar.leftTrigger > 0.5:
            lScale *= 1.15
            if leftMenuPointer['Pressed'] == False:
                leftMenuPointer['Pressed'] = True
                vibration("left", 0.02, "high", 0.5)
                scene.addObject(menuSelectCursor, leftMenuPointer, 1.5,False)
        else:
            leftMenuPointer['Pressed'] = False
        
        leftMenuPointer.localScale = [lScale, lScale, lScale]
        leftMenuPointer['Pos_3'] = leftMenuPointer['Pos_2']
        leftMenuPointer['Pos_2'] = leftMenuPointer['Pos_1']
        leftMenuPointer['Pos_1'] = lHitPoint.copy()
    else:
        leftMenuPointer.visible = False
        leftLineMenu.visible = False
        
def updateVRControllerData():
    gripLocL = xr.controller_grip_location_get(bpy.context,0)
    gripLocR = xr.controller_grip_location_get(bpy.context,1)
    viewerPos = xr.viewer_pose_location
    gripRotL = xr.controller_grip_rotation_get(bpy.context,0)
    gripRotR = xr.controller_grip_rotation_get(bpy.context,1)
    viewerRot = xr.viewer_pose_rotation
                    
    #Assign all the actions to a global variable for easy reading later
    globVar.rightTrigger = xr.action_state_get(bpy.context,'blender_generic','triggers',"/user/hand/right")[0]
    globVar.rightTriggerTouch = xr.action_state_get(bpy.context,'blender_generic','triggers_touch',"/user/hand/right")[0]
    globVar.leftTriggerTouch = xr.action_state_get(bpy.context,'blender_generic','triggers_touch',"/user/hand/left")[0]
    globVar.leftTrigger = xr.action_state_get(bpy.context,'blender_generic','triggers',"/user/hand/left")[0]
    globVar.leftGrip = xr.action_state_get(bpy.context,'blender_generic','grips',"/user/hand/left")[0]
    globVar.rightGrip = xr.action_state_get(bpy.context,'blender_generic','grips',"/user/hand/right")[0]
    globVar.leftStickX = xr.action_state_get(bpy.context,'blender_generic','sticks_x',"/user/hand/left")[0]
    globVar.rightStickX = xr.action_state_get(bpy.context,'blender_generic','sticks_x',"/user/hand/right")[0]
    globVar.leftStickY = xr.action_state_get(bpy.context,'blender_generic','sticks_y',"/user/hand/left")[0]
    globVar.rightStickY = xr.action_state_get(bpy.context,'blender_generic','sticks_y',"/user/hand/right")[0]
    globVar.buttonA = xr.action_state_get(bpy.context,'blender_generic','buttons1',"/user/hand/right")[0]
    globVar.buttonX = xr.action_state_get(bpy.context,'blender_generic','buttons1',"/user/hand/left")[0]
    globVar.buttonB = xr.action_state_get(bpy.context,'blender_generic','buttons2',"/user/hand/right")[0]
    globVar.buttonY = xr.action_state_get(bpy.context,'blender_generic','buttons2',"/user/hand/left")[0]
    globVar.buttonMenu = xr.action_state_get(bpy.context,'blender_generic','button_menu',"/user/hand/left")[0]    
    
def main():
    #If there is no VR Session active
    if str(xr) == "None":
        print("No VR Session Active")
        pass
    else: 
        #Initialization section
        VR_Init()
        updateVRControllerData()   
        
        laser.blenderObject["Attrib_Time"] = VR_Position["Timer"]
        pointerNullL.blenderObject["Attrib_Time"] = VR_Position["Timer"]
        pointerNullR.blenderObject["Attrib_Time"] = VR_Position["Timer"]
        
        if VR_Position["Timer"] > 2 and VR_Position["Timer"] < 2.5:
            feet.restorePhysics()
            #scene.objects['_Config']['Teleport'] = False
        #---------------------End of initialization-------------------------    

        #climbRayCast.worldPosition = xr.viewer_pose_location
        VRCamLocCB(xr.viewer_pose_location)
        VRCamRotCB(xr.viewer_pose_rotation)
        VR_Position_Empty.worldPosition = xr.navigation_location
        VR_Viewer_Empty.worldPosition = viewerPos
        feetRotTemp = mathutils.Quaternion([viewerRot[0], 0, 0, viewerRot[3]])
        feetRotCB(feetRotTemp)
            

        #Copy hands location and stop from trespassing
        handsInteraction()
        
        #Check if hand grabs objects or climb
        climbing()
        handGrabLeft()
        handGrabRight()
        
        #Move using teleport or locomotion
        if bge.logic.move == True:
            motionType()        

        #Stop camera going through selected objects
        stopCameraTresspasing()
        
        #Check if menu is activated
        isMenuActivated()
        
        #Check for any ray touching a Menu
        isMenuRay()
        
        own["Running"] = False
        VR_Position["deltaTime"] = VR_Position["Timer"]
        


        
def Start():      
    xr = bpy.context.window_manager.xr_session_state 
    if 'preDrawCallbackInit' not in own:
        bpy.context.scene.frame_set(0)
        
        #---properties for pre drawing callback---
        VR_Position['navLocation'] = mathutils.Vector([0,0,0])
        VR_Position['copyNavLoc'] = False
        VR_Position['navRotation'] = mathutils.Quaternion([0,0,0,0])
        VR_Position['copyNavRot'] = False
        
        #Left Hand Position and Rotation
        VR_Position['lHandLocation'] = mathutils.Vector([0,0,0])
        VR_Position['copyLHandLoc'] = False
        VR_Position['lHandRotation'] = mathutils.Quaternion([0,0,0,0])
        VR_Position['copyLHandRot'] = False
        
        #Right Hand Position and Rotation
        VR_Position['rHandLocation'] = mathutils.Vector([0,0,0])
        VR_Position['copyRHandLoc'] = False
        VR_Position['rHandRotation'] = mathutils.Quaternion([0,0,0,0])
        VR_Position['copyRHandRot'] = False
        
        #Left Hand Visual Position and Rotation
        VR_Position['lHandVisualLocation'] = mathutils.Vector([0,0,0])
        VR_Position['copyLHandVLoc'] = False
        VR_Position['lHandVisualRotation'] = mathutils.Quaternion([0,0,0,0])
        VR_Position['copyLHandVRot'] = False
        
        #Right Hand Visual Position and Rotation
        VR_Position['rHandVisualLocation'] = mathutils.Vector([0,0,0])
        VR_Position['copyRHandVLoc'] = False
        VR_Position['rHandVisualRotation'] = mathutils.Quaternion([0,0,0,0])
        VR_Position['copyRHandVRot'] = False
        
        #VR camera position and rotation
        VR_Position['VRCamPos'] = mathutils.Vector([0,0,0])
        VR_Position['copyVRCamPos'] = False
        VR_Position['VRCamRot'] = mathutils.Quaternion([0,0,0,0])
        VR_Position['copyVRCamRot'] = False
        
        #Feet position and rotation
        VR_Position['feetLocation'] = mathutils.Vector([0,0,0])
        VR_Position['copyFeetLoc'] = False
        VR_Position['feetLocationXY'] = mathutils.Vector([0,0,0])
        VR_Position['copyFeetLocXY'] = False
        VR_Position['feetRotation'] = mathutils.Quaternion([0,0,0,0])
        VR_Position['copyFeetRot'] = False
        
        #Assing the property to allow movement
        bge.logic.move = True
        #create Dash speed
        bge.logic.dashSpeed = 0
        
        rightMenuPointer['Pos_1'] = mathutils.Vector([0,0,0])
        rightMenuPointer['Pos_2'] = mathutils.Vector([0,0,0])
        rightMenuPointer['Pos_3'] = mathutils.Vector([0,0,0])
        
        leftMenuPointer['Pos_1'] = mathutils.Vector([0,0,0])
        leftMenuPointer['Pos_2'] = mathutils.Vector([0,0,0])
        leftMenuPointer['Pos_3'] = mathutils.Vector([0,0,0])
        
        #bge.logic.openingDoor = False
        bge.logic.knob = 0
        bge.logic.trackObj = scene.objects['HitPos']
        scene.pre_draw.append(copyTransforms)
        own["preDrawCallbackInit"] = True

        
        
    if str(xr) != "None":
        if own["Running"] == False:
            own["Running"] = True
            mainThread = threading.Thread(target=main)
            mainThread.start()
   