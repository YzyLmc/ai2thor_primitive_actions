'''wrapped skills for iThor agent desgined for planning in PDDL'''

import random
from copy import deepcopy
import numpy as np

def No_op(controller):
    event = controller.step('Pass')
    return event

def GoTo(object_or_location_1, object_or_location_2, controller, event):
    '''
    Teleport to a fixed location associated with an object.
    It now only works with FloorPlan203

    '''
    def dist_pose(obj1, obj2):
        x1, y1, z1 = obj1["x"], obj1["y"], obj1["z"]
        x2, y2, z2 = obj2["x"], obj2["y"], obj2["z"]
        p1 = np.array([x1, y1, z1])
        p2 = np.array([x2, y2, z2])
        return np.sqrt(np.sum((p1-p2)**2, axis=0))

    if object_or_location_1 == object_or_location_2: # cannot go to same place
        return False, event
    
    metadata = event.metadata
    event = controller.step('Pass')
    obj = [obj for obj in metadata["objects"] if object_or_location_2 in obj['objectId']][0]
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
    # breakpoint() 
    poses = [p for p in poses if {'x':p['x'], 'y':p['y'], 'z':p['z']} in avail_positions]
    poses = sorted(poses, key=lambda p:dist_pose(p, obj['position']))
    # poses = sorted(avail_positions, key=lambda p:dist_pose(p, obj['position']))
    
    for i in range(len(poses)):
        pose = poses[i]
        pose['horizon'] = 30
        event = controller.step("TeleportFull", **pose)
        if event.metadata["lastActionSuccess"]:
            break
    
    event = controller.step('Pass')
    success = dist_pose(event.metadata['agent']['position'], obj['position']) < 2
    return success, event

def PickUp():
    pass

def PutIn():
    pass

def PlaceOn():
    pass

def Open():
    pass

def Toggle():
    pass

def Empty():
    pass

def Slice():
    pass

def Cook():
    pass

def Slice():
    pass