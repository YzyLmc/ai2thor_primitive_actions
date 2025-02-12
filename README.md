# ai2thor_primitive_actions
Primitive actions in ai2thor simulator. Contains customized skills and scripts for specific tasks for my projects.

## Install ai2thor
install ai2thor simply by
```
pip install ai2thor
```

Installation in a separate virtual environment is recommended.
NOTE: ai2thor environment can be modified (e.g., add objects to a environment) through specific version of Unity. Check [this page](https://github.com/allenai/ai2thor/tree/main/unity) for more information.
## Install Fast Downward

Fast Downward allows convenient planning via PDDL domain and problem files. The goal of having primitive actions is to use them for planning, and all action APIs will be converted into actions in PDDL.

To install Fast Downward, first install the dependencies:

```
sudo apt install cmake g++ make python3
```

Then clone their repo and build the planner by:

```
./build.py
```

Check more optional components in their full [build instruction](https://github.com/aibasel/downward/blob/main/BUILD.md)

To plan with Fast Downward, cd to the root directory `downward/` and specify the domain and problem files:

```
./fast-downward.py /path/to/domain.pddl /path/to/problem.pddl  --search "astar(lmcut())"
```

## Skills
ai2thor consists of multiple modes, and each of them has different features. This repo provides support for the following modes:
- iThor: the vanilla mode which only has high-level actions. We provide wrappers on top of those skills that are more convenient to call and chained together for planning within the domain defined in the PDDL file.
- manipulaThor adds an robot embodiment to the simulator, which allows it to perform low-level actions. We build high-level actions resembling the ones in iThor.
