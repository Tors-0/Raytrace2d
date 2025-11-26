import math

from PIL import Image, ImageDraw

scenePath = "scene.png"
renderPath = "output.png"

# yay physics constants
G = 6.67430E-11
c = 299_792_458
# F_g = GMm/r^2
# a_g = GM/r^2
# but light is funky
# TODO: why is the below wrong (a: somebody on stackexchange was wrong)
# theta = 4GM/c^2/r
# theta from paper = 2GM/c^2/r

try:
    scene = Image.open(scenePath)
    pix = scene.load()
except IOError:
    exit(1)

cameraPt = (48, 75)
# x pos, y pos, mass
gravityObjs = [(159, 65, 1E+26),]
# https://arxiv.org/pdf/physics/0508030
deflectionConstant = 2 * G * gravityObjs[0][2] / c**2
# https://en.wikipedia.org/wiki/Schwarzschild_radius
eventHorizon = 2 * G * gravityObjs[0][2] / c**2
sceneSize = scene.size

deflectionValue = [[]]
for x in range(sceneSize[0]):
    deflectionValue.append([])
    for y in range(sceneSize[1]):
        dist = math.sqrt((x - gravityObjs[0][0]) ** 2 + (y - gravityObjs[0][1]) ** 2)
        if dist != 0:
            deflect = deflectionConstant / dist
        else:
            deflect = 0
        deflectionValue[x].append(deflect)

# ~~find point closest to black hole~~
# step forward, calc deflection, record scene state at pos, repeat
# kill path if hit edge, if within schwarzschild radius of black hole, set all remaining scene states on path to black (path has crossed event horizon)

angleResolution = 14400
sceneStates = [[]]
for angleStep in range(angleResolution):
    sceneStates.append([])
    angle = 2 * math.pi / angleResolution * angleStep
    pos = [cameraPt[0], cameraPt[1]]
    # while (path not dead): move one step along angle, calc deflection & update angle, record scene state at current pos
    pathAlive = 1
    while pathAlive == 1:
        # kill paths that cross the event horizon
        if math.sqrt((pos[0] - gravityObjs[0][0])**2 + (pos[1] - gravityObjs[0][1])**2) < eventHorizon:
            pathAlive = 0

        trajectory_y = math.tan(angle) * (gravityObjs[0][0] - pos[0]) + pos[1]
        # check which side of our projected trajectory the black hole will be on
        if trajectory_y > gravityObjs[0][1]:
            angle -= deflectionValue[math.floor(pos[0])][math.floor(pos[1])]
        else:
            angle += deflectionValue[math.floor(pos[0])][math.floor(pos[1])]

        sceneStates[angleStep].append(pix[(pos[0], pos[1])])
        pos[0] += math.cos(angle)
        pos[1] += math.sin(angle)
        if (pos[0] >= sceneSize[0]) | (pos[1] >= sceneSize[1]) | (pos[0] < 0) | (pos[1] < 0):
            pathAlive = 0

output = Image.new("RGB", sceneSize, (255,255,255))
draw = ImageDraw.Draw(output)
for angleStep in range(angleResolution):
    angle = 2 * math.pi / angleResolution * angleStep
    pos = [cameraPt[0], cameraPt[1]]
    for data in sceneStates[angleStep]:
        if data != (255,255,255):
            draw.point((math.floor(pos[0]), math.floor(pos[1])), data)
        pos[0] += math.cos(angle)
        pos[1] += math.sin(angle)
        if (pos[0] >= sceneSize[0]) | (pos[0] < 0) | (pos[1] >= sceneSize[1]) | (pos[1] < 0):
            break
# draw black circle on black hole
draw.circle([gravityObjs[0][0], gravityObjs[0][1]], eventHorizon, (0,0,0), (255, 0, 0), 1)
# draw green circle on camera
draw.circle(cameraPt, 2, (255,255,255), (0,255,0), 1)
output.save(renderPath)
scene.close()
output.close()
