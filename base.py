import math
from math import degrees

from PIL import Image

scenePath = "scene.png"
renderPath = "render.png"

# yay physics constants
G = 6.67430E-11
c = 299_792_458
# F_g = GMm/r^2
# a_g = GM/r^2
# but light is funky
# theta = 4GM/c^2/r

try:
    scene  = Image.open(scenePath)
except IOError:
    exit(1)

cameraPt = (48, 75)
# x pos, y pos, mass
gravityObjs = [(159, 65, 1.89E+27), (132,  904, 1000)]
sceneSize = scene.size

# ~~find point closest to black hole~~
# step forward, calc deflection, repeat
# kill path if within 2.8m of black hole or hit edge

angleResolution = 45
for angleStep in range(angleResolution):
    angle = 2 * math.pi / angleResolution * angleStep
    # while (path not dead): move one step along angle, calc deflection & update angle, record scene state at current pos
