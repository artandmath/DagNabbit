# DagNabbit

For use on render farms to generate a screenshot of the Nuke DAG (Node Graph).

Target audience: TDs, leads, supervisors for quick visual look at a render script without having to launch nuke. Possible uses in script analysis with machine learning.

Based on code from:

https://github.com/herronelou/nuke_dag_capture

https://community.foundry.com/discuss/topic/160363/pyside2-qt-5-12-threading-inside-nuke-13-2v3-freezing-crashing

![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/DagNabbitDemo.gif)

## Usage
- Install the DagNabbit workspace and DagNabbit.py into the pipeline so that DagNabbit capabale render node(s) can do their thing.
- Implement a farm task that modifies onScriptLoad and runs DagNabbit, or runs DagNabbit in some other manner on an open Nuke GUI.
- Probably want to do this on a DagNabbit specific copy of the script if modifying the script. 
> [!IMPORTANT]
> The render node(s) that use DagNabbit will need to launch the Nuke GUI and will consume a nuke license.

## To do - short/mid term
- Investigate Nuke's --tg command line switch and see if it's possible to invoke the DAG from there. https://learn.foundry.com/nuke/content/comp_environment/configuring_nuke/command_line_operations.html
- ~~Add node class highlighting~~ This can be done by feeding a function to the dictionary key "selectedNodes". eg nuke.allNodes('Tracker4').
- Option to fit image to the dependencies of selected node(s).
- Option to fit image within bounds of a given width/height.
- Settle on a schema and output an accompanying text file with the PNGs.
- Deal with or suppress any pop-ups after script launch that might get in the way of manipulating the DAG window.
- Validate on production quality hardware and a script with a very large DAG.
- Re-implement Erwan's tiling system if we hit limits on a decent box.
- Test Nuke 14, 15.
- Test Windows & Mac.
- Clean up some duplication in the classes. Some classes are doing things that others should. Mayube chunk it down some further.
- Add some code to analyse the overall color of the PNG and up the delay time and re-take the snapshot if the output looks to be blank. (or even better, figure out a method to determine when nuke has finished drawing the DAG)
- Create hooks for arbitary code execution before/after events in the capture pipeline (for node colouring, enabling/disabling expression lines, overload $gui, etc)

## To do - long term
- Link functionality to the Nuke profiler.
- Heatmaps for bounding boxes, CPU time, expressions, callbacks, non-contributing nodes, contents of groups, etc
- Termporal heatmaps, linking the single frame DAG snapshot to data gathered from each frame rendered on the farm.
- Drll down into groups.
- Refactor to be DCC independant and move functionality into a plugin.

## Testing
- Successfully tested under "worst case conditions":
  - Nuke 13.2v9
  - Virtual Machine, 4x i5 cpus, 6 GB ram, 256 MB vram
  - Ubuntu 22.04, KDE Plasma: 5.24.7, KDE Frameworks: 5.92.0, Qt: 5.51.3, Linux kernel: 6.5.0-28-generic (64-bit)
  - preliminary testing with Ubuntu 22.04, Gnome looks like it might work.
- Failed tests:
  - Centos7 Gnome & KDE (fresh install with no updates applied from the v2009 distro)
  - Ubuntu 22.04 Xfce
  - PNGs larger than 7.5k x 8.5k, suspect the 256 MB vram might be the issue

## Walkthrough - example files
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step01.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step02.png)
![screenshot](https://raw.githubusercontent.com/artandmath/DagNabbit/master/docs/step03.png)
