# DagNabbit
Code to capture a render of the Nuke DAG.

For use on render farms to generate a snapshot of the DAG that generated a render.

Target users: TDs, leads, supervisors and machine learning. 

Based on code from https://github.com/herronelou/nuke_dag_capture

## Usage
- the render node(s) on the farm that use DagNabbit will need to launch the GUI and consume a nuke license.
- copy the DagNabbit workspace onto DagNabbit capabale render node(s).
- implement a farm task that modifies onScriptLoad and runs DagNabbit.
- probably want to do this on a DagNabbit specific copy of the script. 

## Todo
- Add node class highlighting.
- Option to fit image to selected node(s) dependencies.
- Option to fit image within bounds of a given width/height.
- Output an accompanying text file with the PNGs.
- Deal with or suppress any pop-ups after nuke launch.

## Longterm
- refactor to be DCC independant and move functionality into a plugin
- drill down into groups

## Testing
- successfully tested under "worst case conditions":
  - Nuke 13.2v9
  - Virtual Machine 6GB ram, 4CPU i5, 256MB VRAM
  - Ubuntu 22.04, KDE Plasma: 5.24.7, KDE Frameworks: 5.92.0, Qt: 5.51.3, Linux kernel: 6.5.0-28-generic (64-bit)
  - preliminary testing with Ubuntu 22.04, Gnome looks like it might work.
- failed tests:
  - Centos7 Gnome & KDE (no upgrades from the v2009 distro)
  - Ubuntu 22.04 Xfce
  - PNGs larger than 8k x 8k, suspect the 256MB VRAM is the issue

![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step01.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step02.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step03.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step04.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step05.png)
