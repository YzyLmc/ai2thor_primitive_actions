'''wrapped skills for iThor agent desgined for planning in PDDL'''

import random
from copy import deepcopy
import numpy as np
from copy import deepcopy
import logging

from ai2thor.util.metrics import get_shortest_path_to_object

def no_op(controller):
    event = controller.step('Pass')
    return event

def step_time(controller, event):
    "simulate time moving forward by one step"
    start_time = event.metadata['currentTime']
    # for _ in range(5):
    #     event = controller.step('Pass')
    event = controller.step('Pass')
    end_time = event.metadata['currentTime']
    return event, 50*(end_time - start_time)

def move(object_or_location, controller, event, realistic=True):
    '''
    Move to a place interactable with the target object/location by teleporting through a trajectory
    '''
    t = 0
    full_name_dict = {
        "sink": "sinkbasin",
        "knife": "butterknife"
    }
    object_or_location = full_name_dict[object_or_location.lower()] if object_or_location.lower() in full_name_dict else object_or_location
    def dist_pose(obj1, obj2):
        x1, y1, z1 = obj1["x"], obj1["y"], obj1["z"]
        x2, y2, z2 = obj2["x"], obj2["y"], obj2["z"]
        p1 = np.array([x1, y1, z1])
        p2 = np.array([x2, y2, z2])
        return np.sqrt(np.sum((p1-p2)**2, axis=0))
    
    metadata = event.metadata
    if "cabinet" in object_or_location.lower() or "drawer" in object_or_location.lower():
        idx = int(object_or_location[-1])
        object_or_location = object_or_location[:-1]
    else:
        idx = 0
    if "countertop" in object_or_location.lower():
        # print([obj['name'] for obj in metadata["objects"] if object_or_location.lower() in obj['objectId'].lower()])
        obj = sorted([obj for obj in metadata["objects"] if object_or_location.lower() in obj['objectId'].lower()], key=lambda d:d['name'])[1]
        # print(obj['name'], object_or_location)
    else:
        obj = sorted([obj for obj in metadata["objects"] if object_or_location.lower() in obj['objectId'].lower()], key=lambda d:d['objectId'])[idx]
    if realistic:
        try:
            init_position = event.metadata['agent']['position']
            init_rotation = event.metadata['agent']['rotation']
            path = get_shortest_path_to_object(controller, obj['objectId'], initial_position=init_position, initial_rotation=init_rotation)[:8]
            # dist_list = [dist_pose(path[i], path[i+1]) for i in range(len(path)-1)]
            # t_weighted_by_length = sum(dist_list)//1.0
            # for _ in range(int(t_weighted_by_length)):
            #     event, t_0 = step_time(controller, event)
            #     t += t_0
            # for pose in path:
            #     event = controller.step("Teleport", position=pose)
            #     event, t_0 = step_time(controller, event)
            #     t += t_0
        except:
            pass
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
    
    for i in range(int(len(poses)/7), len(poses)):
        pose = poses[i]
        pose['horizon'] = 30
        event = controller.step("TeleportFull", **pose)
        if event.metadata["lastActionSuccess"]:
            break
    if event.metadata['errorMessage']:
        logging.info(event.metadata['errorMessage'])

    event = controller.step('Pass')
    # success = dist_pose(event.metadata['agent']['position'], obj['position']) < 2
    event, t_1 = step_time(controller, event)
    t += t_1
    return event, t

def move_object(target_object, target_location, controller, event, follow=True, auto_open=False):
    "Handle edge cases by hardcoding if needed. Now is just regular pick & place"
    "follow :bool: if robot will be ended up at the same location as the object"
    # hardcode some mapping from abbrevs to full name
    t = 0 # timing
    full_name_dict = {
        "sink": "sinkbasin",
        "knife": "butterknife"
    }

    if "toaster" in target_location.lower() and "bread" in target_object.lower() and (not any(['BreadSliced' in o['objectId'] for o in event.metadata['objects']])) and follow == True:
        target_location = random.choice(["CounterTop", "Shelf"])
    if ("stoveburner" in target_location.lower()) and ("pan" not in target_object.lower()):
        target_location = random.choice(["CounterTop", "Shelf", "Sink"])
        
    target_object = full_name_dict[target_object] if target_object in full_name_dict else target_object
    target_location = full_name_dict[target_location.lower()] if target_location.lower() in full_name_dict else target_location
    original_location = deepcopy(target_location)
    if "cabinet" in target_location.lower() or "drawer" in target_location.lower():
        idx = int(target_location[-1])
        target_location = target_location[:-1]
    else:
        idx = 0
    if "countertop" in target_location.lower():
        # print([obj['name'] for obj in event.metadata["objects"] if target_location.lower() in obj['objectId'].lower()])
        location = sorted([o for o in event.metadata["objects"] if target_location.lower() in o['objectId'].lower()], key=lambda d:d['name'])[1]
        # print(location["name"], target_object, target_location)
    else:
        location = sorted([o for o in event.metadata["objects"] if target_location.lower() in o['objectId'].lower()], key=lambda d:d['objectId'])[idx]

    obj_list = [obj for obj in event.metadata["objects"] if target_object.lower() in obj['objectId'].lower()]
    # egg and bread change names after being cracked or sliced, so they are handled in specific ways
    if "bread" in target_object and any(['BreadSliced' in o['objectId'] for o in obj_list]):
        obj = sorted([o for o in event.metadata["objects"] if "BreadSliced".lower() in o['objectId'].lower()], key=lambda d:d['objectId'])[1]
    elif "potato" in target_object and any(['PotatoSliced' in o['objectId'] for o in obj_list]):
        obj = sorted([o for o in event.metadata["objects"] if "PotatoSliced".lower() in o['objectId'].lower()], key=lambda d:d['name'])[1]
    elif "egg" in target_object and any(['EggCracked' in o['objectId'] for o in obj_list]):
        obj = sorted([o for o in event.metadata["objects"] if "EggCracked".lower() in o['objectId'].lower()], key=lambda d:d['objectId'])[0]
    else:
        obj = obj_list[0]
    # location = [o for o in event.metadata["objects"] if target_location.lower() in o['objectId'].lower()][0]

    assert obj['pickupable'] == True, f"{obj['objectId']} has to be pickupable"
    assert location['receptacle'] == True, f"{location['objectId']} has to be receptacle"

    err = []
    auto_opened = False
    if auto_open:
        if (location["openable"]) and (not location["isOpen"]):
            event, _ = open(location['objectId'], controller, event)
            auto_opened = True
    if "shelf" in target_location.lower():
        event = controller.step(
            action="GetSpawnCoordinatesAboveReceptacle",
            objectId=location['objectId'], 
            anywhere=True
        )
        pose = event.metadata["actionReturn"]
        for p in pose:
            p = {"x":p["x"], "y":p["y"] + 0.02, "z":p["z"]}
            event = controller.step(
                action="PlaceObjectAtPoint",
                objectId=obj["objectId"],
                position=p,
            )
            if event.metadata["lastActionSuccess"]:
                break
        err.append(event.metadata["errorMessage"])
    elif "pan" in target_location.lower() or "plate" in target_location.lower():
        # location = [o for o in event.metadata["objects"] if target_location in o['objectId'].lower()][0]
        poses = [{'objectName':o['name'], "position":o['position'], "rotation": o['rotation']} for o in event.metadata['objects'] if not o['objectId'] == obj['objectId']]
        # if "drawer" in target_location.lower():
        #     poses.append({'objectName':obj['name'], "position":{'x': location['position']['x'], 'y': location['position']['y'] + 0.05 , 'z': location['position']['z']}})
        if "bread" in target_object.lower() or "potato" in target_object.lower():
            poses.append({'objectName':obj['name'], "position":{'x': location['position']['x'], 'y': location['position']['y'] + 0.2, 'z': location['position']['z']}, "rotation": {"y":0, "x":90, "z":0}})
        else:
            poses.append({'objectName':obj['name'], "position":{'x': location['position']['x'], 'y': location['position']['y'] + 0.1 , 'z': location['position']['z']}})
        event = controller.step('SetObjectPoses',objectPoses = poses, placeStationary=False)
        for _ in range(10):
            event = no_op(controller)
    else:
        # if "knife" in target_object.lower():
        #     event = controller.step(
        #         action="RotateHeldObject",
        #         pitch=90,
        #     )
        event = controller.step(
            action="PickupObject",
            objectId=obj['objectId'],
            forceAction=True
        )
        err.append(event.metadata["errorMessage"])

        event_put = controller.step(
            action="PutObject",
            objectId=location['objectId'],
            forceAction=True,
            placeStationary=True
        )
        if not event_put.metadata["lastActionSuccess"]:
            event = controller.step(
                action="GetSpawnCoordinatesAboveReceptacle",
                objectId=location['objectId'], 
                anywhere=True
            )
            pose = event.metadata["actionReturn"]
            for p in pose:
                p = {"x":p["x"], "y":p["y"] + 0.02, "z":p["z"]}
                event = controller.step(
                    action="PlaceObjectAtPoint",
                    objectId=obj["objectId"],
                    position=p,
                )
                if event.metadata["lastActionSuccess"]:
                    break
            err.append(event_put.metadata["errorMessage"])
    event, t_i = step_time(controller, event)
    t += t_i
    if auto_opened:
        event = close(location['objectId'], controller, event)

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
    if follow:
        event, t_move = move(original_location, controller, event)
        t += t_move
        err.append(event.metadata["errorMessage"])
    if any(err):
        print(target_object, target_location)
        print(err)
    event = no_op(controller)
    return event, t

def put_bread_in_toaster(target_object, target_location, controller, event):
    # event, t = move(target_location, controller, event)
    event, t = move_object(target_object, target_location, controller, event)
    return event, t

def put_mug_in_machine(target_object, target_location, controller, event):
    # event, t = move(target_location, controller, event)
    event, t = move_object(target_object, target_location, controller, event)
    return event, t

def open(openable, controller, event):
    # obj = [obj for obj in event.metadata["objects"] if openable.lower() in obj['objectId'].lower()][0]
    if ("cabinet" in openable.lower() or "drawer" in openable.lower()) and (not "|" in openable):
        idx = int(openable[-1])
        openable = openable[:-1]
    else:
        idx = 0
    obj = sorted([obj for obj in event.metadata["objects"] if openable.lower() in obj['objectId'].lower()], key=lambda d:d['objectId'])[idx]
    assert obj['openable'] == True, f"{obj['objectId']} has to be openable"
    event = controller.step(
        action="OpenObject",
        objectId=obj['objectId'],
        openness=1,
        forceAction=True
    )
    event, t = step_time(controller, event)
    return event, t

# Not used in this project
def close(openable, controller, event):
    if ("cabinet" in openable.lower() or "drawer" in openable.lower()) and not "|" in openable:
        idx = int(openable[-1])
        openable = openable[:-1]
    else:
        idx = 0
    obj = sorted([obj for obj in event.metadata["objects"] if openable.lower() in obj['objectId'].lower()], key=lambda d:d['objectId'])[idx]
    assert obj['openable'] == True, f"{obj['objectId']} has to be openable"
    event = controller.step(
        action="CloseObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    event, t = step_time(controller, event)
    return event, t

def turn_on(toggleable, controller, event):
    full_name_dict = {
        "stoveburner": "StoveKnob",
        "sink": "faucet"
    }
    toggleable = full_name_dict[toggleable] if toggleable in full_name_dict else toggleable
    # obj = [obj for obj in event.metadata["objects"] if toggleable.lower() in obj['objectId'].lower()][idx]
    obj_list = sorted([obj for obj in event.metadata["objects"] if toggleable.lower() in obj['objectId'].lower()], key=lambda d:d['objectId'])
    assert obj_list[0]['toggleable'] == True, f"{obj_list[0]['objectId']} has to be toggleable"
    # turn on all stoveburner
    if "stoveburner" in toggleable:
        for obj in obj_list:
            event = controller.step(
                action="ToggleObjectOn",
                objectId=obj['objectId'],
                forceAction=True
            )
    else:
        event = controller.step(
                action="ToggleObjectOn",
                objectId=obj_list[0]['objectId'],
                forceAction=True
            )
    event, t = step_time(controller, event)
    return event, t

def empty_liquid(pourable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if pourable.lower() in obj['objectId'].lower()][0]
    assert obj['canFillWithLiquid'] == True, f"{obj['objectId']} has to be fillable with liquid"
    event = controller.step(
        action="EmptyLiquidFromObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    event, t = step_time(controller, event)
    return event, t

def fill_liquid(pourable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if pourable.lower() in obj['objectId'].lower()][0]
    assert obj['canFillWithLiquid'] == True, f"{obj['objectId']} has to be fillable with liquid"
    event = controller.step(
        action="FillObjectWithLiquid",
        objectId=obj['objectId'],
        fillLiquid="wine",
        forceAction=True
    )
    event, t = step_time(controller, event)
    return event, t

def slice(sliceable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if sliceable.lower() in obj['objectId'].lower()][0]
    event, t = move(sliceable, controller, event)
    assert obj['sliceable'] == True, f"{obj['objectId']} has to be sliceable"
    event = controller.step(
        action="SliceObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    event, t = step_time(controller, event)
    return event, t

def crack_egg(egg, controller, event):
    obj = [obj for obj in event.metadata["objects"] if egg.lower() in obj['objectId'].lower()][0]
    assert "Egg".lower() in obj['name'].lower(), f"{obj['objectId']} has to be egg"
    event = controller.step(
        action="BreakObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    event, t = step_time(controller, event)
    return event, t

def clean(dirtyable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if dirtyable.lower() in obj['objectId'].lower()][0]
    assert obj['dirtyable'] == True, f"{obj['objectId']} has to be dirtyable"
    event = controller.step(
        action="CleanObject",
        objectId=obj['objectId'],
        forceAction=True
    )
    event, t = step_time(controller, event)
    return event, t

def dirty(dirtyable, controller, event):
    obj = [obj for obj in event.metadata["objects"] if dirtyable.lower() in obj['objectId'].lower()][0]
    assert obj['dirtyable'] == True, f"{obj['objectId']} has to be dirtyable"
    event = controller.step(
        action="DirtyObject",
        objectId=obj['objectId'],
        forceAction=False
    )
    event, t = step_time(controller, event)
    return event, t

def make_omelet(egg, potato, bread, plate, controller, event):
    "Rearrange egg, bread, and potato in the plate"
    objects = event.metadata['objects']
    plate = [obj for obj in event.metadata["objects"] if plate in obj['objectId'].lower()][0]
    # event, t = move(plate, controller, event)
    # no bread in omelet
    # assert "bread" in bread and any(['BreadSliced' in o['objectId'] for o in objects])
    # bread = [o for o in event.metadata["objects"] if "BreadSliced".lower() in o['objectId'].lower()][1]
    assert "potato" in potato and any(['PotatoSliced' in o['objectId'] for o in objects])
    potato = [o for o in event.metadata["objects"] if "PotatoSliced".lower() in o['objectId'].lower()][1] # to avoid the larger chunk of potato slice...
    assert "egg" in egg and any(['EggCracked' in o['objectId'] for o in objects])
    egg = [o for o in event.metadata["objects"] if "EggCracked".lower() in o['objectId'].lower()][0]
    
    # bread first, then egg, and potato on top
    poses = [{'objectName':obj['name'], "position":obj['position'], "rotation": obj['rotation']} for obj in event.metadata['objects'] if not any([obj['name'] == o['name'] for o in [egg, potato]])]
    # poses.append({'objectName':bread['name'], "position":{'x': plate['position']['x'], 'y': plate['position']['y'] + 0.1, 'z': plate['position']['z']}, "rotation": {"y":270, "x":270, "z":270}})
    poses.append({'objectName':egg['name'], "position":{'x': plate['position']['x'], 'y': plate['position']['y'] + 0.2 , 'z': plate['position']['z']}})
    poses.append({'objectName':potato['name'], "position":{'x': plate['position']['x'], 'y': plate['position']['y'] + 0.3, 'z': plate['position']['z']}, "rotation": {"y":0, "x":90, "z":0}})
    event = controller.step('SetObjectPoses',objectPoses = poses, placeStationary=False)
    event = move("plate", controller, event)

    for _ in range(10):
        event = no_op(controller)

    event, t = step_time(controller, event)
    return event, t
    