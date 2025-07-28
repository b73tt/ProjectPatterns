#!/usr/bin/env cached-nix-shell
#!nix-shell -p python3 python3Packages.pillow python3Packages.pygame python3Packages.opencv4 python3Packages.toml -i python3


import pygame, sys, xml.etree.ElementTree as ET
import cv2, numpy as np, toml, os
from PIL import Image

SETTINGS_FILE = os.path.expanduser("~/.config/ProjectPatterns.toml")
if os.path.exists(SETTINGS_FILE):
	settings = toml.load(open(SETTINGS_FILE))
else:
	settings = {}

# Projector dimensions
if "projectorres" in settings:
	(w,h) = settings["projectorres"]
else:
	w,h = 640,480
	settings["projectorres"] = (w,h)

# cutting mat dimensions
if "cuttingmat" in settings:
	(cw,ch) = settings["cuttingmat"]
else:
	cw,ch = 420,270
	settings["cuttingmat"] = (cw,ch)

# pre saved warping
if "selectedcoords" in settings:
	selectedcoords = settings["selectedcoords"]
else:
	selectedcoords = {"tl": (0,0), "tr":(w,0), "bl":(0,h), "br":(w,h)}

# you might want a different order of picking points than anticlockwise
if "coordorder" in settings:
	coordorder = settings["coordorder"]
else:
	coordorder = ["tl", "bl", "br", "tr"]
	settings["coordorder"] = coordorder

# might as well save the inverted flag since I'm doing everything else
if "inverted" in settings:
	inverted = settings["inverted"]
else:
	inverted = False
	settings["inverted"] = inverted


# start the display
pygame.init()
display = pygame.display.set_mode((w,h))
pygame.display.set_caption("c=calibrate, i=invert, q=quit")

# read SVG
img = pygame.image.load(sys.argv[1])
xml = ET.parse(sys.argv[1]).getroot()
xpixpermm = img.get_size()[0] / float(xml.get("width").replace("mm",""))
ypixpermm = img.get_size()[1] / float(xml.get("height").replace("mm",""))

# Cutting mat sample points
xsamples = (0, int(cw*xpixpermm))
ysamples = (0, int(ch*ypixpermm))



def displayImage(display, img, source, dest, inverted):
	# convert pygame image (pygame can read SVGs) to CV2 image (CV2 can do good transforms)
	cimg = np.array(Image.frombytes("RGBA", img.get_size(), pygame.image.tostring(img, "RGBA", False)))

	# flip the image if "i" has been pressed
	if inverted:
		cimg = 255-cimg

	# Figure out the perspective transform maths
	pts = np.float32(np.array((source["bl"], source["br"], source["tr"], source["tl"])).tolist())
	dst_pts = np.float32(np.array((dest["bl"], dest["br"], dest["tr"], dest["tl"])).tolist())
	M = cv2.getPerspectiveTransform(pts, dst_pts)

	# do the transform
	cimg = cv2.warpPerspective(cimg, M, dsize = (w,h), flags = cv2.INTER_LINEAR)

	# display the new image to the screen
	display.blit(pygame.image.frombuffer(cimg[:,:,:3].tobytes(), cimg.shape[1::-1], "RGB") , (0,0))
	pygame.display.update()

boardcoords = {"tl": (xsamples[0],ysamples[0]), "tr":(xsamples[1], ysamples[0]), "bl":(xsamples[0], ysamples[1]), "br":(xsamples[1], ysamples[1])}

# initial display of the image
displayImage(display, img, boardcoords, selectedcoords, inverted)

select = 0
calibrating = False
while True:
	event = pygame.event.wait()
	if event.type == pygame.QUIT:
		break
	if event.type == pygame.MOUSEBUTTONUP and calibrating:
		pos = pygame.mouse.get_pos()
		selectedcoords[coordorder[select]] = pos
		select = (select + 1) % len(coordorder)

		displayImage(display, img, boardcoords, selectedcoords, inverted)
		pygame.display.set_caption(coordorder[select])
	if event.type == pygame.KEYDOWN:
		if event.key == pygame.K_c:
			calibrating = not calibrating
			if calibrating:
				select = 0
				pygame.display.set_caption(coordorder[select])
				pygame.mouse.set_cursor(pygame.cursors.broken_x)
			else:
				pygame.display.set_caption("c=calibrate, i=invert, q=quit")
				pygame.mouse.set_cursor(pygame.cursors.arrow)
		elif event.key == pygame.K_i:
			inverted = not inverted
			displayImage(display, img, boardcoords, selectedcoords, inverted)
		elif event.key == pygame.K_q:
			break


settings["selectedcoords"] = selectedcoords
settings["inverted"] = inverted
toml.dump(settings, open(SETTINGS_FILE, "w"))
