#!/usr/bin/env bash

xrandr --output HDMI-0 --mode 640x480
$(dirname "$0")/project.py "$1"
xrandr --output HDMI-0 --off

