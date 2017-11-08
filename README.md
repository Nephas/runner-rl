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
  <img src="https://github.com/Nephas/runner-rl/blob/master/levelgen.bmp" width="600"/>
</p>

Other features implemented so far:

* basic rendering
* player character movement and field of view
* simple world interactions (door opening, pushing)
* light sources
* mouse movement

Light and shadows are completely dynamic and interact with changes in the environment like 
opening doors and moving scenery.

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/screen.png" width="750"/>
</p>
