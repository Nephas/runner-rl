# RUNNER
a Cyberpunk Roguelike


**Teaser**

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/gif/demo.gif" width="900"/>
</p>

*Game Prototype: a cyberpunk roguelike of stealth, hacking and evil megacorps*

There is a [Design Document](https://github.com/Nephas/runner-rl/blob/master/docs/design.pdf) to 
outline the creative vision.

At the moment there is mostly a 'physics engine' and a level generator:

Level generation:
It produces levels as abstract tree of rooms at different tiers. The player starts on 
the outermost tier of the tree and moves towards a central 'goal room' which will enable 
placement of progressively strong enemies, items and key finding 'puzzles.

The outer tiers are interconnected via airducts to mix up the boring tree structure.
Levels are scattered with interconnected Servers and Terminals which will later on interact 
with the level objects.

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/gif/levelgen.gif" width="500"/>
</p>

Other features implemented so far:

* basic rendering
* player character movement and field of view
* simple world interactions (door opening, pushing)
* light sources
* simple physics
* mouse movement and panels
* basic AI behaviour
* dialogue tree system

Light and shadows are completely dynamic and interact with changes in the environment like 
opening doors and moving scenery. The physics engine can handle simple elements like Fluids, 
Gases, Fire and environmental destruction. Also, blood.

Last, but definitely not least: Credits for the really promising tileset got to Reddit user [Gzintu](https://www.reddit.com/user/gzintu).

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/graphics/exp_24x24.png" width="384"/>
</p>
