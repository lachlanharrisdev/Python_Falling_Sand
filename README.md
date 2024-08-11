# Overview
A small python project experimenting with cellular automata & eventually turning it into a game.

# Features
- Unique simulation for powders, fluids & gases on a cell-based grid
- Simulation for reactions, used to create unique particles
- Decay simulation where particles will turn into another over a period of time (used to make some realistic reactions like burning wood & evaporated water turning back into rain)
- Density simulation where particles will float above adjacent particles if they have a lower density, vice versa (works with gases too!)
- Currently 13 unique elements, each with their own density, colour, reactants, movement type, and more)
- Expandable, open-source framework to easily add more CA rules, particle types & reactions, etc.
- Built-in sound effects for all elements, played at appropriate times (during reactions, being placed manually or when their velocity changes)
- [EXPERIMENTAL] objectives system with currently 3 unique objective types
- [EXPERIMENTAL] custom, modular dialogue boxes to complement the objectives system

# Installation & Controls
Simply download all the code & have all the python files within the same folder, then run main.py.

- Pressing left click will place the selected particle
- Pressing right click will delete the hovered particle(s)
- Using the minus & equals keys to change the cursor size
- Press the C key to change particle

# Known Bugs
- The entire gases system lol (expect some wacky stuff when playing with them)
