# Project Patterns

Use a cheap projector to project SVGs life-sized on a cutting surface.

Usage:

```./project.py FILE.svg```

or

```./project.sh FILE.svg```

(you'll probably need to modify the .sh file to suit your setup - it enables/disables the projector display using xrandr)

You can invert colours by pressing "i".

To enter (and leave) calibration mode, press "c".
In calibration mode the cursor will turn into a cross and you'll need to click the corners of your cutting mat anti-clockwise starting from top left.
If your cutting mat is a different size to mine, you'll need to specify its dimensions in the .config/ProjectPatterns.toml file.

Press "q" to quit.


## Actually using this as someone other than me

If you're not running NixOS, replace the first 2 lines of project.py with ```#!/usr/bin/env python3``` and make sure you have the packages in line 2 installed
