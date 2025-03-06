import random
import os
from PIL import Image

from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
from ithor_skills import *
import time
def capture_obs(controller, file_prefix, no_img_log):
    import os
    from PIL import Image
    counter = 1
    directory = f"video/Toast/trial_15_SPOP_PR/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    f_list = os.listdir(directory)
    if f_list:
        nums = [int(f.split("_")[0]) for f in f_list]
        counter = max(nums) + 1
    else:
        counter = 0
    # screenshot_path = f"{counter}_{file_prefix}.jpg"
    event = controller.step('Pass')
    im = Image.fromarray(event.frame)
    im.save(f"{directory}{counter}_{file_prefix}.jpg")
    if not no_img_log:
        logging.info(f"# screenshot saved to {counter}_{file_prefix}.jpg")
    return f"{directory}{counter}_{file_prefix}.jpg"

# init ai2thor controller
controller = Controller(
    massThreshold = 1,
    scene = "FloorPlan1",
    snapToGrid=False,
    visibilityDistance=1.5,
    gridSize=0.1,
    renderDepthImage=True,
    renderInstanceSegmentation=True,
    renderObjectImage = True,
    width= 1080,
    height= 1080,
    fieldOfView=100,
    # platform=CloudRendering,
            )
event = no_op(controller)
for obj in [obj for obj in event.metadata["objects"] if 'WineBottle' in obj['objectId']]:
    event = controller.step('RemoveFromScene', objectId=obj["objectId"])

for obj in [obj for obj in event.metadata["objects"] if 'Kettle' in obj['objectId']]:
    event = controller.step('RemoveFromScene', objectId=obj["objectId"])

for obj in [obj for obj in event.metadata["objects"] if 'Stool' in obj['objectId']]:
    event = controller.step('RemoveFromScene', objectId=obj["objectId"])


event, _ = move_object("butterknife", "Drawer1", controller, event, follow=False, auto_open=True)
event, _ = move_object("DishSponge", "Sink", controller, event, follow=False, auto_open=True)
event, _ = move_object("Egg", "Fridge", controller, event, follow=False, auto_open=True)
event, _ = move_object("Mug", "Cabinet1", controller, event, follow=False, auto_open=True)
event, _ = move_object("Bread", "Shelf", controller, event, follow=False, auto_open=True)
event, _ = move_object("Potato", "Fridge", controller, event, follow=False, auto_open=True)
event, _ = move_object("Apple", "Cabinet3", controller, event, follow=False, auto_open=True)
event, _ = move_object("Tomato", "Cabinet4", controller, event, follow=False, auto_open=True)
event, _ = move_object("saltshaker", "Fridge", controller, event, follow=False, auto_open=True)
event, _ = move_object("CreditCard", "Drawer2", controller, event, follow=False, auto_open=True)
event, _ = move_object("PepperShaker", "Drawer6", controller, event, follow=False, auto_open=True)
event, _ = fill_liquid("Mug", controller, event)
event, _ = move_object("Plate", "CounterTop", controller, event, follow=False, auto_open=True)
event, _ = move_object("Pan", "StoveBurner", controller, event, follow=False, auto_open=True)
event, _ = move("Drawer5", controller, event)
controller.step(
    action="RotateRight",
    degrees=90
)
controller.step("MoveBack")
controller.step("MoveLeft", moveMagnitude=0.8)
controller.step("Pass")

breakpoint()
######### START

for _ in range(9):
    event = controller.step(
                action="RotateLeft",
                degrees=10
            )
# screenshot_path = capture_obs(controller, f"init_$0$", no_img_log=False)
for _ in range(18):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")

for _ in range(9):
    event = controller.step(
                action="RotateLeft",
                degrees=10
            )

for _ in range(30):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")

for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
controller.step("Pass")
# breakpoint()
time.sleep(2)
#################### MOVE TO SHELF
for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
for _ in range(10):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateLeft",
                degrees=10
            )
controller.step("Pass")
# breakpoint()
time.sleep(2)
####################### MOVE TO COUNTERTOP
for _ in range(1):
    controller.step(
        action="MoveBack",
        moveMagnitude=None
    )
    controller.step("Pass")
for _ in range(2):
    controller.step(
        action="MoveLeft",
        moveMagnitude=None
    )
    controller.step("Pass")
time.sleep(2)
###################### MOVE TO DRAWER1
event, t = open('drawer1', controller, event)
# breakpoint()
time.sleep(2)
######################### OPEN DRAWER1
for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
event = controller.step('Pass')
for _ in range(25):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")

# breakpoint()
time.sleep(2)
######################## MOVE TO SINK
for _ in range(18):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
for _ in range(30):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
obj = [obj for obj in event.metadata["objects"] if 'bread'.lower() in obj['objectId'].lower()][0]
event = controller.step(
            action="PickupObject",
            objectId=obj['objectId'],
            forceAction=True,
        )
controller.step("Pass")
# pick up the bread
# breakpoint()
for _ in range(1):
    controller.step(
        action="MoveBack",
        moveMagnitude=None
    )
    controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
for _ in range(10):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateLeft",
                degrees=10
            )
for _ in range(2):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    controller.step("Pass")
controller.step("Pass")
# move to counter top
obj = sorted([o for o in event.metadata["objects"] if 'countertop'.lower() in o['objectId'].lower()], key=lambda d:d['name'])[1]
controller.step(
    action="PutObject",
    objectId=obj['objectId'],
    forceAction=True,
    placeStationary=True
)
controller.step("Pass")
# breakpoint()
time.sleep(2)
########################################## MOVE_OBJ BREAD COUNTERTOP
for _ in range(3):
    controller.step(
        action="MoveLeft",
        moveMagnitude=None
    )
    controller.step("Pass")
obj = [obj for obj in event.metadata["objects"] if 'butterknife'.lower() in obj['objectId'].lower()][0]
event = controller.step(
            action="PickupObject",
            objectId=obj['objectId'],
            forceAction=True,
        )
for _ in range(3):
    controller.step(
        action="MoveRight",
        moveMagnitude=None
    )
    controller.step("Pass")
obj = sorted([o for o in event.metadata["objects"] if "countertop".lower() in o['objectId'].lower()], key=lambda d:d['name'])[1]
controller.step(
    action="PutObject",
    objectId=obj['objectId'],
    forceAction=True,
    placeStationary=True
)
event = controller.step("Pass")
# breakpoint()
time.sleep(2)
####################### MOVE_OBJECT KNIFE COUNTERTOP
event = controller.step("Pass")
time.sleep(2)
####################### MOVE COUNTERTOP
obj = [obj for obj in event.metadata["objects"] if 'bread'.lower() in obj['objectId'].lower()][0]
event = controller.step(
            action="SliceObject",
            objectId=obj['objectId'],
            forceAction=True,
        )
# breakpoint()
time.sleep(2)
####################### SLICE BREAD
obj = sorted([o for o in event.metadata["objects"] if "BreadSliced".lower() in o['objectId'].lower()], key=lambda d:d['objectId'])[1]
event = controller.step(
            action="PickupObject",
            objectId=obj['objectId'],
            forceAction=True,
        )
for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
for _ in range(18):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
for _ in range(17):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateLeft",
                degrees=10
            )
obj = sorted([o for o in event.metadata["objects"] if "toaster".lower() in o['objectId'].lower()], key=lambda d:d['name'])[0]
controller.step(
    action="PutObject",
    objectId=obj['objectId'],
    forceAction=True,
    placeStationary=True
)
# breakpoint()
time.sleep(2)
########################## PUT_BREAD_IN_TOASTER
event = controller.step("Pass")
time.sleep(2)
########################## MOVE TO TOASTER
event, t = turn_on('toaster', controller, event)
time.sleep(2)
########################## TURN ON TOASTER
obj = sorted([o for o in event.metadata["objects"] if "BreadSliced".lower() in o['objectId'].lower()], key=lambda d:d['objectId'])[1]
event = controller.step(
            action="PickupObject",
            objectId=obj['objectId'],
            forceAction=True,
        )
for _ in range(9):
    event = controller.step(
                action="RotateLeft",
                degrees=10
            )
for _ in range(17):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateLeft",
                degrees=10
            )
for _ in range(22):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
for _ in range(9):
    event = controller.step(
                action="RotateRight",
                degrees=10
            )
for _ in range(4):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
location = sorted([o for o in event.metadata["objects"] if "plate".lower() in o['objectId'].lower()], key=lambda d:d['objectId'])[0]
poses = [{'objectName':o['name'], "position":o['position'], "rotation": o['rotation']} for o in event.metadata['objects'] if not o['objectId'] == obj['objectId']]

poses.append({'objectName':obj['name'], "position":{'x': location['position']['x'], 'y': location['position']['y'] + 0.2, 'z': location['position']['z']}, "rotation": {"y":0, "x":90, "z":0}})
event = controller.step('SetObjectPoses',objectPoses = poses, placeStationary=False)
for _ in range(10):
    event = no_op(controller)
time.sleep(2)
########################## MOVE_OBJECT BREAD PLATE
for _ in range(2):
    controller.step(
        action="MoveAhead",
        moveMagnitude=None
    )
    event = controller.step("Pass")
time.sleep(2)
#########################MOVE COUNTERTOP
