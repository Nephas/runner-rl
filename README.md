<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/graphics/title.gif" width="450"/>
</p>

*a Cyberpunk Roguelike of stealth, hacking and evil megacorps*

Important Materials:

* [Design Document](https://github.com/Nephas/runner-rl/blob/master/docs/design.pdf)
* [Fiction Teaser](https://github.com/Nephas/runner-rl/blob/master/docs/shortstory1.pdf)
* [Roadmap](https://github.com/Nephas/runner-rl/blob/master/TODO.md)

Pre-pre-alpha, very not stable:
No Balancing, no win state, random crashes. Consider it more of a tech demo.

[Recent Build - linux 64bit](https://www.dropbox.com/sh/j2y4j3cbhl8xmsk/AAAhrOxCWBeJh5O1b-hxDkALa?dl=0&preview=linux_64.tar)



At the moment there is mostly a 'physics engine' and a level generator:

Level generation:
It produces levels as abstract tree of rooms at different tiers. The player starts on 
the outermost tier of the tree and moves towards a central 'goal room' which will enable 
placement of progressively strong enemies, items and key finding 'puzzles.

The outer tiers are interconnected via airducts to mix up the boring tree structure.
Levels are scattered with interconnected Servers and Terminals which will later on interact 
with the level objects.

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/presentation/levelgen.gif" width="500"/>
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

**Teaser**

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/presentation/screen.png" width="900"/>
</p>

Light and shadows are completely dynamic and interact with changes in the environment like 
opening doors and moving scenery. The physics engine can handle simple elements like Fluids, 
Gases, Fire and environmental destruction. Also, blood.

Last, but definitely not least: Credits for the really promising tileset got to Reddit user [Gzintu](https://www.reddit.com/user/gzintu).

<p align="left">
  <img src="https://github.com/Nephas/runner-rl/blob/master/graphics/exp_24x24.png" width="384"/>
</p>
