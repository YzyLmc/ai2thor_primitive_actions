'''wrapped skills for iThor agent desgined for planning in PDDL'''

import random
from copy import deepcopy
import numpy as np

from ai2thor.util.metrics import get_shortest_path_to_point

def no_op(controller):
    event = controller.step('Pass')
    return event

def move(object_or_location, controller, event):
    '''
    Move to a place interactable with the target object/location by teleporting through a trajectory
    '''
    full_name_dict = {
        "sink": "sinkbasin"
    }
    object_or_location = full_name_dict[object_or_location.lower()] if object_or_location.lower() in full_name_dict else object_or_location
    def dist_pose(obj1, obj2):
        x1, y1, z1 = obj1["x"], obj1["y"], obj1["z"]
        x2, y2, z2 = obj2["x"], obj2["y"], obj2["z"]
        p1 = np.array([x1, y1, z1])
        p2 = np.array([x2, y2, z2])
        return np.sqrt(np.sum((p1-p2)**2, axis=0))
    
    metadata = event.metadata
    obj = [obj for obj in metadata["objects"] if object_or_location.lower() in obj['objectId'].lower()][0] # only take the first in the list if there are multiple
    avail_positions = controller.step(
        action="GetReachablePositions"
    ).metadata["actionReturn"]
    event = controller.step(
        action="GetInteractablePoses",
        objectId=obj['objectId'],
        horizons=np.linspace(-30, 0),
        standings=[True]
    )
    poses = event.metadata["actionReturn"]
    poses = [p for p in poses if {'x':p['x'], 'y':p['y'], 'z':p['z']} in avail_positions]
    poses = sorted(poses, key=lambda p:dist_pose(p, obj['position']))
    
    for i in range(len(poses)):
        pose = poses[i]
        pose['horizon'] = 30
        event = controller.step("TeleportFull", **pose)
        if event.metadata["lastActionSuccess"]:
            break
    if event.metadata['errorMessage']:
        print(event.metadata['errorMessage'])

    event = controller.step('Pass')
    # success = dist_pose(event.metadata['agent']['position'], obj['position']) < 2
    return event

def move_object(target_object, target_location, controller, event):
    "Handle edge cases by hardcoding if needed. Now is just regular pick & place"
    # hardcode some mapping from abbrevs to full name
    full_name_dict = {
        "sink": "sinkbasin"
    }
    target_object = full_name_dict[target_object] if target_object in full_name_dict else target_object
    target_location = full_name_dict[target_location.lower()] if target_location.lower() in full_name_dict else target_location
    obj_list = [obj for obj in event.metadata["objects"] if target_object.lower() in obj['objectId'].lower()]
    # egg and bread change names after being cracked or sliced, so they are handled in specific ways
    if "bread" in target_object and any(['BreadSliced' in o['objectId'] for o in obj_list]):
        obj = [o for o in event.metadata["objects"] if "BreadSliced".lower() in o['objectId'].lower()][1]
    elif "potato" in target_object and any(['PotatoSliced' in o['objectId'] for o in obj_list]):
        obj = [o for o in event.metadata["objects"] if "PotatoSliced".lower() in o['objectId'].lower()][1] # to avoid the larger chunk of potato slice...
    elif "egg" in target_object and any(['EggCracked' in o['objectId'] for o in obj_list]):
        obj = [o for o in event.metadata["objects"] if "EggCracked".lower() in o['objectId'].lower()][0]
    else:
        obj = obj_list[0]
    location = [o for o in event.metadata["objects"] if target_location.lower() in o['objectId'].lower()][0]
    assert obj['pickupable'] == True, f"{obj['objectId']} has to be pickupable"
    assert location['receptacle'] == True, f"{location['objectId']} has to be receptacle"

    err = []
    if "pan" in target_location.lower() or "plate" in target_location.lower():
        event = controller.step(
            action="GetSpawnCoordinatesAboveReceptacle",
            objectId=location['objectId'], 
            anywhere=True
        )
        pose = event.metadata["actionReturn"]
        for p in pose:
            event = controller.step(
                action="PlaceObjectAtPoint",
                objectId=obj["objectId"],
                position=p
            )
            if event.metadata["lastActionSuccess"]:
                break
        err.append(event.metadata["errorMessage"])
    else:
        event = controller.step(
            action="PickupObject",
            objectId=obj['objectId'],
            forceAction=True
        )
        err.append(event.metadata["errorMessage"])

        event = controller.step(
            action="PutObject",
            objectId=location['objectId'],
            forceAction=True,
            placeStationary=True
        )
        err.append(event.metadata["errorMessage"])

    # event = controller.step(
    #         action="PickupObject",
    #         objectId=obj['objectId'],
    #         forceAction=True
    #     )

    # event = controller.step(
    #     action="PutObject",
    #     objectId=location['objectId'],
    #     forceAction=True,
    #     placeStationary=True
    # )

    # if not event.metadata["lastActionSuccess"]:
    #     event = controller.step(
    #         action="GetSpawnCoordinatesAboveReceptacle",
    #         objectId=location['objectId'], 
    #         anywhere=True
    #     )
    #     pose = event.metadata["actionReturn"]
    #     for p in pose:
    #         event = controller.step(
    #             action="PlaceObjectAtPoint",
    #             objectId=obj["objectId"],
    #             position=p
    #         )
    #         if event.metadata["lastActionSuccess"]:
    #             break
    #     err.append(event.metadata["errorMessage"])
    
    event = move(location['objectId'], controller, event)
    err.append(event.metadata["errorMessage"])
    if any(err):
        print(err)
    event = no_op(controller)
    return event

def open(openable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if openable.lower() in obj['objectId'].lower()][0]
    assert obj['openable'] == True, f"{obj['objectId']} has to be openable"
    event = controller.step(
        action="OpenObject",
        objectId=obj['objectId'],
        openness=1,
        forceAction=True
    )
    return event

# Not used in this project
# def close(openable, controller, event):
#     obj = [obj for obj in event.metadata["objects"] if openable in obj['objectId']][0]
#     assert obj['openable'] == True, f"{obj['objectId']} has to be openable"
#     event = controller.step(
#         action="CloseObject",
#         objectId=obj['objectId'],
#         forceAction=True
#     )
#     return event

def turn_on(toggleable, controller, event):
    full_name_dict = {
        "stoveburner": "stoveknob"
    }
    toggleable = full_name_dict[toggleable] if toggleable in full_name_dict else toggleable
    obj = [obj for obj in event.metadata["objects"] if toggleable.lower() in obj['objectId'].lower()][0]
    assert obj['toggleable'] == True, f"{obj['objectId']} has to be toggleable"
    event = controller.step(
        action="ToggleObjectOn",
        objectId=obj['objectId'],
        forceAction=True
    )

    return event

def empty_liquid(pourable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if pourable.lower() in obj['objectId'].lower()][0]
    assert obj['canFillWithLiquid'] == True, f"{obj['objectId']} has to be fillable with liquid"
    event = controller.step(
        action="EmptyLiquidFromObject",
        objectId=obj['objectId'],
        forceAction=False
    )
    return event

def slice(sliceable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if sliceable.lower() in obj['objectId'].lower()][0]
    assert obj['sliceable'] == True, f"{obj['objectId']} has to be sliceable"
    event = controller.step(
        action="SliceObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    return event

def crack_egg(egg, controller, event):
    obj = [obj for obj in event.metadata["objects"] if egg.lower() in obj['objectId'].lower()][0]
    assert "Egg".lower() in obj['name'].lower(), f"{obj['objectId']} has to be egg"
    event = controller.step(
        action="BreakObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    return event

def clean(dirtyable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if dirtyable.lower() in obj['objectId'].lower()][0]
    assert obj['dirtyable'] == True, f"{obj['objectId']} has to be dirtyable"
    event = controller.step(
        action="CleanObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    return event

def dirty(dirtyable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if dirtyable.lower() in obj['objectId'].lower()][0]
    assert obj['dirtyable'] == True, f"{obj['objectId']} has to be dirtyable"
    event = controller.step(
        action="DirtyObject",
        objectId=obj['objectId'],
        forceAction=False
    )
    return event

# def cook(cookable, controller, event):
#     pass

def make_omelet(egg, potato, bread, plate, controller, event):
    "Rearrange egg, bread, and potato in the plate"
    objects = event.metadata['objects']
    plate = [obj for obj in event.metadata["objects"] if plate in obj['objectId'].lower()][0]
    assert "bread" in bread and any(['BreadSliced' in o['objectId'] for o in objects])
    bread = [o for o in event.metadata["objects"] if "BreadSliced".lower() in o['objectId'].lower()][1]
    assert "potato" in potato and any(['PotatoSliced' in o['objectId'] for o in objects])
    potato = [o for o in event.metadata["objects"] if "PotatoSliced".lower() in o['objectId'].lower()][1] # to avoid the larger chunk of potato slice...
    assert "egg" in egg and any(['EggCracked' in o['objectId'] for o in objects])
    egg = [o for o in event.metadata["objects"] if "EggCracked".lower() in o['objectId'].lower()][0]
    
    # bread first, then egg, and potato on top
    poses = [{'objectName':obj['name'], "position":obj['position'], "rotation": obj['rotation']} for obj in event.metadata['objects'] if not any([obj['name'] == o['name'] for o in [egg, bread, potato]])]
    poses.append({'objectName':bread['name'], "position":{'x': plate['position']['x'], 'y': plate['position']['y'] + 0.1, 'z': plate['position']['z']}, "rotation": {"y":270, "x":270, "z":270}})
    poses.append({'objectName':egg['name'], "position":{'x': plate['position']['x'], 'y': plate['position']['y'] + 0.2 , 'z': plate['position']['z']}})
    poses.append({'objectName':potato['name'], "position":{'x': plate['position']['x'], 'y': plate['position']['y'] + 0.3, 'z': plate['position']['z']}, "rotation": {"y":0, "x":90, "z":0}})
    event = controller.step('SetObjectPoses',objectPoses = poses, placeStationary=False)
    event = move("plate", controller, event)
    for _ in range(10):
        event = no_op(controller)
    return event