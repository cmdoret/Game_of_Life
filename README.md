# Game_of_Life
A small game written in python we made for a school project.
This is based on Conway's game of life, with added features:
- Addition different colors, competing against each other.
- Changing the rules of birth/survival/death for each color independently
- Hybridization: Two colors can hybridize if a tile fullfils the requirements to be born in both colors and the difference of their indexes is 2. This is just for fun, see the script for more details.
The "seed" file is used to store seeds. New seeds can be added or removed via the GUI.
The "default" file contains a set of seeds. It should not be deleted, as it is used as a backup in case something happened to the "seed" file.
When the program is run, a "data" file will be generated. This file contains the number of tiles of each color at every iteration in the last simulation. It can be used to make plots, allowing to visualize the progress of each color through time.

