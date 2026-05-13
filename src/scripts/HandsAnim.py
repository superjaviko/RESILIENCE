import bge

scene = bge.logic.getCurrentScene()
cont = bge.logic.getCurrentController()
own = bge.logic.getCurrentController().owner

def main():
    if scene.objects["VR_Position"]["Timer"] > 2.1:
        LeftHand = scene.objects["LeftTouchVisual"]
        RightHand = scene.objects["RightTouchVisual"]

        LeftFistCollision = scene.objects["LeftFistCollision"]
        LeftFingerCollision = scene.objects["LeftFingerCollision"]

        RightFistCollision = scene.objects["RightFistCollision"]
        RightFingerCollision = scene.objects["RightFingerCollision"]

        Animation = cont.actuators["Animation"]
#        if str(bge.logic.trackObj) == 'None':
#            bge.logic.knob = 0

        if own["Side"] == "Left":
            if bge.logic.leftGrip > 0.7:
                if bge.logic.leftTrigger == 0:
                    own["Action"] = "Pointing"
                    LeftFingerCollision.restorePhysics()
                    LeftFistCollision.suspendPhysics()
                else:
                    own["Action"] = "Closed"
                    LeftFistCollision.restorePhysics()
                    LeftFingerCollision.suspendPhysics()
            elif bge.logic.leftGrip < 0.7:
                own["Action"] = "Open"
                LeftFistCollision.suspendPhysics()
                LeftFingerCollision.suspendPhysics()
                #if str(bge.logic.trackObj) == 'LeftFistCollision':
#                if bge.logic.knob == 1:
#                    #LeftHand.removeParent()
#                    bge.logic.trackObj = scene.objects['HitPos']
#                    bge.logic.knob = 0

        else:
            if bge.logic.rightGrip > 0.7:
                if bge.logic.rightTrigger == 0:
                    own["Action"] = "Pointing" 
                    RightFingerCollision.restorePhysics()
                    RightFistCollision.suspendPhysics()
                else:
                    own["Action"] = "Closed"
                    RightFistCollision.restorePhysics()
                    RightFingerCollision.suspendPhysics()

            elif bge.logic.rightGrip < 0.7:
                own["Action"] = "Open"
                RightFistCollision.suspendPhysics()
                RightFingerCollision.suspendPhysics()
                #if str(bge.logic.trackObj) == 'RightFistCollision':
#                if bge.logic.knob == 2:
#                    #RightHand.removeParent()
#                    bge.logic.trackObj = scene.objects['HitPos']
#                    bge.logic.knob = 0
        
        if bge.logic.rightGrip < 0.7 and bge.logic.leftGrip < 0.7 and bge.logic.knob > 0:
            bge.logic.trackObj = scene.objects['HitPos']
            bge.logic.knob = 0
        if own["Action"] == "Open":
            Animation.frameStart = 10
            Animation.frameEnd = 10
        if own["Action"] == "Closed":
            Animation.frameStart = 13
            Animation.frameEnd = 13
        if own["Action"] == "Pointing":
            Animation.frameStart = 16
            Animation.frameEnd = 16

        cont.activate("Animation")
main()