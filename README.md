# DagNabbit

For use on render farms to generate a screenshot of the Nuke DAG (Node Graph).

Target audience: TDs, leads, supervisors for quick visual look at a render script without having to launch nuke. Possible uses in script analysis with machine learning.

Based on code from https://github.com/herronelou/nuke_dag_capture

## Usage
- The render node(s) on the farm that use DagNabbit will need to launch the GUI and will consume a nuke license.
- Install the DagNabbit workspace and DagNabbit.py onto DagNabbit capabale render node(s).
- Implement a farm task that modifies onScriptLoad and runs DagNabbit, or runs DagNabbit in some other manner on an open Nuke GUI.
- Probably want to do this on a DagNabbit specific copy of the script. 

## Todo short/mid term
- Clean up some duplication in the classes
- Add node class highlighting. (This can be done currently by feeding a selection to the dictionary key "selectedNodes")
- Option to fit image to the dependencies of selected node(s).
- Option to fit image within bounds of a given width/height.
- Settle on a schema and output an accompanying text file with the PNGs.
- Deal with or suppress any pop-ups after script launch that might get in the way of manipulating the DAG window.

## Todo long term
- refactor to be DCC independant and move functionality into a plugin
- link functionality to the Nuke profiler
- drill down into groups

## Walkthrough, example files
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step01.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step02.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step03.png)

## Testing
- successfully tested under "worst case conditions":
  - Nuke 13.2v9
  - Virtual Machine, 4x i5 cpus, 6 GB ram, 256 MB vram
  - Ubuntu 22.04, KDE Plasma: 5.24.7, KDE Frameworks: 5.92.0, Qt: 5.51.3, Linux kernel: 6.5.0-28-generic (64-bit)
  - preliminary testing with Ubuntu 22.04, Gnome looks like it might work.
- failed tests:
  - Centos7 Gnome & KDE (no upgrades from the v2009 distro)
  - Ubuntu 22.04 Xfce
  - PNGs larger than 7.5k x 8.5k, suspect the 256 MB vram might be the issue
