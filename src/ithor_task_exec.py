'''Execute iThor tasks and take screenshots'''
'Convert generated tasks into python script'
from inspect import getmembers, isfunction, signature
import sys
import os
import argparse
import json

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
    commands.append('event, _ = move("tomato", controller, event)')
    # process the dictionary
    robot_nav_command = None
    for prefix, value in predicate_dict.items():
        try:
            val_0, pred = prefix.split('_')
        except:
            continue
        # tricky if-else logic handles different predicates
        if pred in predicates:
            if pred == "at-location": # the only predicate takes two arguments
                if val_0.lower() == "robot": 
                    robot_nav_command = f'event, _ = move("{value}", controller, event)'
                    command = ""
                else:
                    val_0 = "saltshaker" if val_0.lower() == "lettuce" else val_0
                    command = f'event, _ = {predicates[pred]}("{val_0}", "{value}", controller, event, follow=False, auto_open=True)'
                commands.append(command)
            else: # unary predicates
                value = not value if pred == "is-clean" else value # mapping from 'is-clean' to 'dirty' is reversed
                if value:
                    command = f'event, _ = {predicates[pred]}("{val_0}", controller, event)'
                    commands.append(command)
    if robot_nav_command:
        commands.append(robot_nav_command)
    return commands

def convert_task_to_code(task_name, task, save_dir="plans"):
    'task: {"initial_state":dict, "plan":list}'
    initial_state = task["initial_state"]
    commands = task["plan"]
    
    template = f'''
import numpy as np
import random
import os
from PIL import Image

from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
from ithor_skills import *

def capture_obs(controller, file_prefix):
    import os
    from PIL import Image
    counter = 1
    directory = f"{save_dir}/{task_name}/"
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
    fieldOfView=100,
    platform=CloudRendering,
            )
event = no_op(controller)
for obj in [obj for obj in event.metadata["objects"] if 'WineBottle' in obj['objectId']]:
    event = controller.step('RemoveFromScene', objectId=obj["objectId"])

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
                formatted_command = f'event, time = {function_str}'

                formatted_commands.append(formatted_command)
                formatted_commands.append(f'screenshot_path = capture_obs(controller, f"{command}_${{time}}$")')
                executable = True
                break
        if not executable:
            formatted_commands.append(f'screenshot_path = capture_obs(controller, "{command}_$0$")')


    formatted_code = "\n".join(formatted_commands)
    return template + init_env_code + formatted_code + "\ncontroller.stop()"

def main():
    with open(args.json_file_path) as f:
        tasks_all = json.load(f)
    for goal, tasks in tasks_all.items():
        tasks = {k: v for i, (k, v) in enumerate(tasks_all.items()) if i < args.first_n} if args.first_n > 0 else tasks
        for task_name, task in tasks.items():
            # separately specify different task name and content from the json file
            # {task_name:{initial_state:dict, plan: {SPOP_PR:list, FD_LOM_PR:list }}}
            # ->
            # {task_name_SPOP_PR:{initial_state:dict, plan:list}} + {task_name_FD_LOM_PR:{initial_state:dict, plan:list}}
            for method_name in task["plan"].keys():
                task_name_sub = f"{goal}/{task_name}_{method_name}"
                task_sub = {"initial_state": task["initial_state"], "plan":task["plan"][method_name]}
                generated_code = convert_task_to_code(task_name_sub, task_sub, save_dir=args.save_directory)
                exec(generated_code)
                # calculate time for each task
                f_list_task = os.listdir(f"{args.save_directory}/{task_name_sub}")
                t = sum([float(f.split("$")[1]) for f in f_list_task])
                os.rename(
                    f"{args.save_directory}/{task_name_sub}",
                    f"{args.save_directory}/{task_name_sub}_${round(t, 4)}$"
                )
                print(f"{goal}/{task_name}_{method_name} is done.")
                print(f"total time: {round(t, 4)} sec")
        # calculate time for every goal, e.g., omelet, toast,...

        f_list_goal = os.listdir(f"{args.save_directory}/{goal}")
        t_FD = 0
        t_SPOP = 0
        for f_goal in f_list_goal:
            if "FD" in f_goal:
                t_FD += float(f_goal.split("$")[1])
            elif "SPOP" in f_goal:
                t_SPOP += float(f_goal.split("$")[1])
        os.rename(
            f"{args.save_directory}/{goal}",
            f"{args.save_directory}/{goal}_SPOP_${round(t_SPOP, 4)/(len(f_list_goal)/2)}$_FD_${round(t_FD, 4)/(len(f_list_goal)/2)}$"
        )
        print(f"{goal} is done.")
        print(f"On average, SPOP takes {round(t_SPOP, 4)/(len(f_list_goal)/2)}")
        print(f"On average, FD takes {round(t_FD, 4)/(len(f_list_goal)/2)}")
        print('\n\n\n')

    # count avg time


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_file_path", type=str)
    parser.add_argument("--save_directory", type=str, default="plans/")
    parser.add_argument("--first_n", type=int, default=0)
    args = parser.parse_args()
    main()
    # commands = [
    #     "(move robot cabinet1)",
    #     "(open robot cabinet1)",
    #     "(open robot drawer1)",
    #     "(open robot drawer2)",
    #     "(open robot drawer3)",
    #     "(move robot sink)",
    #     "(turn-on robot sink)",
    #     "(move-object robot mug countertop)",
    #     "(put-mug-in-machine robot mug coffeemachine)",
    #     "(turn-on robot coffeemachine)",
    #     "(make-coffee robot coffeemachine mug)"
    # ]
    # initial_state = {
    #     "Robot_at-location": "Cabinet1",
    #             "Knife_at-location": "Drawer1",
    #             "DishSponge_at-location": "Sink",
    #             "Egg_at-location": "Fridge",
    #             "Mug_at-location": "Cabinet1",
    #             "Bread_at-location": "Shelf",
    #             "Potato_at-location": "Fridge",
    #             "Apple_at-location": "Cabinet3",
    #             "Tomato_at-location": "Drawer2",
    #             # "Lettuce_at-location": "Drawer4",
    #             "CreditCard_at-location": "Drawer4",
    #             "PepperShaker_at-location": "Cabinet2",
    #             "coffee-made": False,
    #             "omelet-made": False,
    #             "toast-made": False,
    #             "breakfast-made": False,
    #             "Mug_is-full": False,
    #             "Bread_is-cooked": False,
    #             "Potato_is-cooked": False,
    #             "Egg_is-cooked": False,
    #             "Bread_is-sliced": False,
    #             "Potato_is-sliced": False,
    #             "Egg_is-cracked": False,
    #             "Mug_is-cracked": False,
    #             "Mug_is-clean": True,
    #             "CounterTop_is-closed": False,
    #             "StoveBurner_is-closed": False,
    #             "Shelf_is-closed": False,
    #             "Sink_is-closed": False,
    #             "Fridge_is-closed": True,
    #             "Toaster_is-closed": False,
    #             "CoffeeMachine_is-closed": False,
    #             "Microwave_is-closed": True,
    #             "Pan_is-closed": False,
    #             "Plate_is-closed": False,
    #             "Cabinet1_is-closed": True,
    #             "Cabinet2_is-closed": True,
    #             "Cabinet3_is-closed": True,
    #             "Drawer1_is-closed": True,
    #             "Drawer2_is-closed": True,
    #             "Drawer3_is-closed": True,
    #             "Drawer4_is-closed": True,
    #             "Toaster_is-on": False,
    #             "CoffeeMachine_is-on": False,
    #             "StoveBurner_is-on": False,
    #             "Microwave_is-on": False,
    #             "Sink_is-on": False,
    #             "Knife_reachable": True,
    #             "DishSponge_reachable": True,
    #             "Egg_reachable": False,
    #             "Mug_reachable": False,
    #             "Bread_reachable": True,
    #             "Potato_reachable": False,
    #             "Apple_reachable": False,
    #             "Tomato_reachable": False,
    #             "Lettuce_reachable": False,
    #             "CreditCard_reachable": False,
    #             "PepperShaker_reachable": False,
    #             "Plate_at-location": "CounterTop",
    #             "Pan_at-location": "StoveBurner"
    # }
    # task = {"initial_state":initial_state, "plan": commands}
    # task_name = "test_1"
    # generated_code = convert_task_to_code(task_name, task)
    # print(generated_code)
    # breakpoint()
    # exec(generated_code)