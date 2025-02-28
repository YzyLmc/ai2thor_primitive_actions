'''Execute iThor tasks and take screenshots'''
'Convert generated tasks into python script'
from inspect import getmembers, isfunction, signature
import sys
import ithor_skills

def initialize_env(predicate_dict):
    "Modified the environment so it satisfied the predicate specifications"
    "This function will return multiple lines of python code in string to be inserted after the main template"
    predicates = {
        "at-location": "move_object", 
        "is-full": "fill_liquid", 
        "is-sliced": "slice", 
        # "is-cracked",
        "is-clean": "dirty", 
        # "is-closed": "open", 
        "is-on": "turn_on"
        }
    
    commands = []
    # process the dictionary
    for prefix, value in predicate_dict.items():
        try:
            val_0, pred = prefix.split('_')
        except:
            continue
        # tricky if-else logic handles different predicates
        if pred in predicates:
            if pred == "at-location": # the only predicate takes two arguments
                if val_0.lower() == "robot": 
                    command = f'event = move("{value}", controller, event)'
                else:
                    command = f'event = {predicates[pred]}("{val_0}", "{value}", controller, event, follow=False, auto_open=True)'
                commands.append(command)
            else: # unary predicates
                value = not value if pred == "is-clean" else value # mapping from 'is-clean' to 'dirty' is reversed
                if value:
                    command = f'event = {predicates[pred]}("{val_0}", controller, event)'
                    commands.append(command)
    return commands

def convert_task_to_code(task_name, task):
    'task: {"initial_state":dict, "plan":list}'
    initial_state = task["initial_state"]
    commands = task["plan"]
    
    template = f'''
import numpy as np
import random
import os
from PIL import Image

from ai2thor.controller import Controller

from ithor_skills import *

def capture_obs(controller, file_prefix):
    counter = 1
    directory = f"plans/{task_name}/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    f_list = os.listdir(directory)
    if f_list:
        nums = [int(f.split("_")[0]) for f in f_list]
        counter = max(nums) + 1
    else:
        counter = 0
    screenshot_path = f"{{counter}}_{{file_prefix}}.jpg"
    event = controller.step('Pass')
    im = Image.fromarray(event.frame)
    im.save(f"{{directory}}{{counter}}_{{file_prefix}}.jpg")
    print(f"Screenshot saved to {{counter}}_{{file_prefix}}.jpg")
    return f"{{directory}}{{counter}}_{{file_prefix}}.jpg"

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
    fieldOfView=100
            )
event = no_op(controller)
'''
    # skill_list = [a[0] for a in getmembers(sys.modules['ithor_skills'], isfunction)]
    skill_list = {a[0]:a[1] for a in getmembers(sys.modules['ithor_skills'], isfunction)}

    init_env = initialize_env(initial_state)
    init_env_code = "\n".join(init_env)

    formatted_commands = ["\n"]
    
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
    return template + init_env_code + formatted_code

if __name__ == "__main__":
    # commands = [
    #     "(open robot drawer)",
    #     "(move-object robot dishsponge sink)",
    #     "(move-object robot knife countertop)",
    #     "(move robot cabinet)",
    #     "(open robot cabinet)",
    #     "(move-object robot bread countertop)",
    #     "(move-object robot potato countertop)",
    #     "(slice robot potato countertop knife)",
    #     "(slice robot bread countertop knife)",
    #     "(move-object robot bread toaster)",
    #     "(turn-on robot toaster)",
    #     "(toast-bread robot bread toaster)",
    #     "(move robot faucet)",
    #     "(turn-on robot faucet)",
    #     "(move robot fridge)",
    #     "(open robot fridge)",
    #     "(move robot sink)",
    #     "(clean robot mug sink dishsponge faucet)",
    #     "(move-object robot mug coffeemachine)",
    #     "(turn-on robot coffeemachine)",
    #     "(make-coffee robot coffeemachine mug)",
    #     "(move-object robot bread plate)",
    #     "(move-object robot egg pan)",
    #     "(move-object robot potato pan)",
    #     "(move robot stoveburner)",
    #     "(turn-on robot stoveburner)",
    #     "(cook-potato robot potato pan stoveburner)",
    #     "(crack-egg robot egg pan stoveburner)",
    #     "(cook-egg robot egg pan stoveburner)",
    #     "(move-object robot egg plate)",
    #     "(move-object robot potato plate)",
    #     "(move robot countertop)",
    #     "(make-omelet robot egg potato bread plate countertop)",
    #     "(make-toast robot bread plate countertop)",
    #     "(make-breakfast )",
    # ]
    commands = [
        "(move robot cabinet)",
        "(open robot cabinet)",
        "(move robot countertop)",
        "(move robot sink)",
        "(move robot fridge)",
        "(open robot fridge)",
        "(move robot drawer)",
        "(open robot drawer)",
        # "(move-object robot bread toaster)",
        "(move robot faucet)",
        "(turn-on robot faucet)",
        "(move robot sink)",
        "(empty-liquid robot mug sink)",
        "(clean robot mug sink dishsponge faucet)",
        "(move-object robot mug coffeemachine)",
        "(move robot coffeemachine)",
        "(turn-on robot coffeemachine)",
        "(make-coffee robot coffeemachine mug)",
        "(move-object robot egg pan)",
        "(move-object robot knife countertop)",
        "(move-object robot potato countertop)",
        "(move robot countertop)",
        "(slice robot potato countertop knife)",
        "(move-object robot potato pan)",
        "(move robot stoveburner)",
        "(crack-egg robot egg pan stoveburner)",
        "(turn-on robot stoveburner)",
        "(cook-egg robot egg pan stoveburner)",
        "(cook-potato robot potato pan stoveburner)",
        "(move-object robot potato plate)",
        "(move-object robot egg plate)",
        "(move robot countertop)",
        "(make-omelet robot egg potato bread plate countertop)",
        "(move-object robot bread countertop)",
        "(move robot countertop)",
        "(slice robot bread countertop knife)",
        "(move-object robot bread toaster)",
        "(move robot toaster)",
        "(turn-on robot toaster)",
        "(toast-bread robot bread toaster)",
        "(move-object robot bread plate)",
        "(move robot countertop)",
        "(make-toast robot bread plate countertop)",
        "(make-breakfast )"
    ]
    initial_state = {
        "Robot_at-location": "Shelf",
        "Knife_at-location": "Sink",
        "DishSponge_at-location": "Sink",
        "Egg_at-location": "Fridge",
        "Mug_at-location": "Sink",
        "Bread_at-location": "Shelf",
        "Potato_at-location": "Fridge",
        "coffee-made": False,
        "omelet-made": False,
        "toast-made": False,
        "breakfast-made": False,
        "Mug_is-full": True,
        "Bread_is-cooked": False,
        "Potato_is-cooked": False,
        "Egg_is-cooked": False,
        "Bread_is-sliced": False,
        "Potato_is-sliced": False,
        "Egg_is-cracked": False,
        "Mug_is-cracked": False,
        "Mug_is-clean": False,
        "Knife_is-clean": True,
        "Cabinet_is-closed": True,
        "Drawer_is-closed": True,
        "CounterTop_is-closed": False,
        "StoveBurner_is-closed": False,
        "Shelf_is-closed": False,
        "Sink_is-closed": False,
        "Fridge_is-closed": True,
        "Toaster_is-closed": False,
        "CoffeeMachine_is-closed": False,
        "Faucet_is-closed": False,
        "Microwave_is-closed": True,
        "Pan_is-closed": False,
        "Plate_is-closed": False,
        "Toaster_is-on": False,
        "CoffeeMachine_is-on": False,
        "Faucet_is-on": False,
        "StoveBurner_is-on": False,
        "Microwave_is-on": False,
        "Knife_reachable": True,
        "DishSponge_reachable": True,
        "Egg_reachable": False,
        "Mug_reachable": True,
        "Bread_reachable": True,
        "Potato_reachable": False,
        "Plate_at-location": "CounterTop",
        "Pan_at-location": "StoveBurner"
    }
    task = {"initial_state":initial_state, "plan": commands}
    task_name = "test_1"
    generated_code = convert_task_to_code(task_name, task)
    print(generated_code)
    breakpoint()
    exec(generated_code)