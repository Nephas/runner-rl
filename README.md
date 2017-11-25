# runner-rl
Game Prototype: a cyberpunk roguelike of stealth, hacking and evil megacorps

At the moment there is mostly a 'physics engine':

A level generator:
It produces levels as abstract tree of rooms at different tiers. The player starts on 
the outermost tier of the tree and moves towards a central 'goal room' which will enable 
placement of progressively strong enemies, items and key finding 'puzzles.

The outer tiers are interconnected via airducts to mix up the boring tree structure.
Levels are scattered with interconnected Servers and Terminals which will later on interact 
with the level objects.

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/levelgen.gif" width="500"/>
</p>

Other features implemented so far:

* basic rendering
* player character movement and field of view
* simple world interactions (door opening, pushing)
* light sources
* simple physics
* mouse movement

Light and shadows are completely dynamic and interact with changes in the environment like 
opening doors and moving scenery. The physics engine can handle simple elements like Fluids, 
Gases, Fire and environmental destruction.

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/gif/demo.gif" width="750"/>
</p>

The gif shows shooting some Fuel Barrels, shooting a lightbulb, then setting the fuel on fire.
later, I'm placing a bomb and blow a hole in the wall towards the server room on the right.
