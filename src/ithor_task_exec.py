'''Execute iThor tasks and take screenshots'''
'Convert generated tasks into python script'
from inspect import getmembers, isfunction, signature
import sys
import ithor_skills

skills = ['move', 'move_object', 'open', 'close', 'turn_on', 'empty_liquid', 'slice', 'crack', 'clean', 'make_omelet']
def convert_task_to_code(commands):
    'task: str: sequence of commands separate by \n'
    template = '''
import numpy as np
import random
import os
from PIL import Image

from ai2thor.controller import Controller

from ithor_skills import *

def capture_obs(controller, file_prefix):
    counter = 1
    directory = f"plans/test/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    f_list = os.listdir(directory)
    if f_list:
        nums = [int(f.split("_")[0]) for f in f_list]
        counter = max(nums) + 1
    else:
        counter = 0
    screenshot_path = f"{counter}_{file_prefix}.jpg"
    event = controller.step('Pass')
    im = Image.fromarray(event.frame)
    im.save(f"{directory}{counter}_{file_prefix}.jpg")
    print(f"Screenshot saved to {counter}_{file_prefix}.jpg")
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
    fieldOfView=90
            )
event = no_op(controller)

event = move_object('pan','stoveburner', controller, event)
event = move_object('plate','countertop', controller, event)
event = move_object('mug','sink', controller, event)
event = dirty('mug', controller, event)


event = move("drawer", controller, event)
'''
    # skill_list = [a[0] for a in getmembers(sys.modules['ithor_skills'], isfunction)]
    skill_list = {a[0]:a[1] for a in getmembers(sys.modules['ithor_skills'], isfunction)}

    formatted_commands = []
    
    commands = [c[1:-1].replace("-", "_") for c in commands] # remove brackets
    for command in commands:
        # if any([command.startswith(skill) for skill in skill_list]):
        executable = False
        for skill_name, function in skill_list.items():
            if command.split(" ")[0] == skill_name:
                args = command.split(" ")
                args = [arg.strip() for arg in args] # first one is always 'robot'
                sig = signature(function) # signature of the function
                params = args[2:len(sig.parameters)]
                params_str = ",".join([f"'{p}'" for p in params])
                function_str = f"{skill_name}({params_str}, controller, event)"
                formatted_command = f'event = {function_str}'

                formatted_commands.append(formatted_command)
                formatted_commands.append(f'screenshot_path = capture_obs(controller, "{command}")')
                executable = True
                break
        if not executable:
            formatted_commands.append(f'screenshot_path = capture_obs(controller, "{command}")')


    formatted_code = "\n".join(formatted_commands)
    return template + formatted_code

if __name__ == "__main__":
    task = [
        "(open robot drawer)",
        "(move-object robot dishsponge sink)",
        "(move-object robot knife countertop)",
        "(move robot cabinet)",
        "(open robot cabinet)",
        "(move-object robot bread countertop)",
        "(move-object robot potato countertop)",
        "(slice robot potato countertop knife)",
        "(slice robot bread countertop knife)",
        "(move-object robot bread toaster)",
        "(turn-on robot toaster)",
        "(toast-bread robot bread toaster)",
        "(move robot faucet)",
        "(turn-on robot faucet)",
        "(move robot fridge)",
        "(open robot fridge)",
        "(move robot sink)",
        "(clean robot mug sink dishsponge faucet)",
        "(move-object robot mug coffeemachine)",
        "(turn-on robot coffeemachine)",
        "(make-coffee robot coffeemachine mug)",
        "(move-object robot bread plate)",
        "(move-object robot egg pan)",
        "(move-object robot potato pan)",
        "(move robot stoveburner)",
        "(turn-on robot stoveburner)",
        "(cook-potato robot potato pan stoveburner)",
        "(crack-egg robot egg pan stoveburner)",
        "(cook-egg robot egg pan stoveburner)",
        "(move-object robot egg plate)",
        "(move-object robot potato plate)",
        "(move robot countertop)",
        "(make-omelet robot egg potato bread plate countertop)",
        "(make-toast robot bread plate countertop)",
        "(make-breakfast )",
    ]
    generated_code = convert_task_to_code(task)
    print(generated_code)
    breakpoint()
    exec(generated_code)