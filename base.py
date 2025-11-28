import math
import pygame
import pygame.gfxdraw
from PIL import Image, ImageDraw

# modify these
scenePath = "scene.png"
# stars.png camera point 92, 90
# scene.png, scene2.png camera point 48, 75
renderPath = "output.png"
tracerPath = "tracer.png"
angleResolution = 360000
# origin is at top left corner, measured in pixels
cameraPt = (48, 75)
# x pos, y pos, mass
#pixels, pixels, kilograms
gravityObjs = [(165, 51, 1.9E+26),]
nodataBackgroundColor = (255,255,255)
tracerScale = 2

# should we generate the tracer debug image
DEBUG_TRACER = False
# should the tracer image contain the path each ray would take without gravitational deflection
DEBUG_TRACER_RAYS = False
# should the tracer image contain the path each ray takes
DEBUG_TRACER_PATHS = True
# /modify these

# DO NOT MODIFY
if not DEBUG_TRACER:
    DEBUG_TRACER_RAYS = False
    DEBUG_TRACER_PATHS = False
# /DO NOT MODIFY

# yay, physics constants
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
    icon = pygame.image.load('./logo.png')
    pix = scene.load()
except IOError:
    exit(1)

# https://arxiv.org/pdf/physics/0508030
deflectionConstant = 2 * G * gravityObjs[0][2] / c**2
# https://en.wikipedia.org/wiki/Schwarzschild_radius
eventHorizon = 2 * G * gravityObjs[0][2] / c**2
print(eventHorizon)
eventHorizonColor = (255-nodataBackgroundColor[0],255-nodataBackgroundColor[1],255-nodataBackgroundColor[2])
sceneSize = scene.size

# pygame setup
pygame.init()
pygame.display.set_caption('Raytrace2d by Tors-0 :: Black Hole')
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(sceneSize, pygame.SCALED | pygame.RESIZABLE)
screen.fill(nodataBackgroundColor)
clock = pygame.time.Clock()

deflectionValue = []
for x in range(sceneSize[0]):
    deflectionValue.append([])
    for y in range(sceneSize[1]):
        dist = math.sqrt((x - gravityObjs[0][0]) ** 2 + (y - gravityObjs[0][1]) ** 2)
        if dist != 0:
            deflect = deflectionConstant / dist
        else:
            deflect = 0
        deflectionValue[x].append(deflect)

angleStepRads = 2 * math.pi / angleResolution

if DEBUG_TRACER:
    pathTrace = Image.new("HSV", (sceneSize[0] * tracerScale, sceneSize[1] * tracerScale), (0, 0, 0))
    pathDraw = ImageDraw.Draw(pathTrace)

output = Image.new("RGB", sceneSize, nodataBackgroundColor)
draw = ImageDraw.Draw(output)

# sceneStates: list[list[tuple[int, int, int]]] = []
for (angleStep) in range(angleResolution):
    # sceneStates.append([])
    angle = angleStepRads * angleStep
    pos = [cameraPt[0], cameraPt[1]]
    # while (path not dead): move one step along angle, calc deflection & update angle, record scene state at current pos
    pathAlive = 1
    if DEBUG_TRACER_PATHS:
        pathColor = (angleStep % 255, 128, 255)

    # step forward, lookup deflection, record scene state at pos, repeat
    # kill path if hit edge, if within schwarzschild radius of black hole, set all remaining scene states on path to black (path has crossed event horizon)
    counter: int = 0
    startAngle: float = angle
    while pathAlive == 1:
        # kill paths that cross the event horizon
        if math.sqrt((pos[0] - gravityObjs[0][0])**2 + (pos[1] - gravityObjs[0][1])**2) <= eventHorizon:
            pathAlive = 0 # kill path
            # sceneStates[angleStep].append(eventHorizonColor) # put a black pixel on the end of the path

            if (pos[0] < sceneSize[0]) and (pos[0] >= 0) and (pos[1] < sceneSize[1]) and (pos[1] >= 0):
                screen.set_at((int(counter * math.cos(startAngle)), int(counter * math.sin(startAngle))), eventHorizonColor)
                if DEBUG_TRACER_RAYS:
                    pathDraw.point((math.floor(pos[0] * tracerScale), math.floor(pos[1] * tracerScale)), (0, 0, 255))

                draw.point((math.floor(pos[0]), math.floor(pos[1])), eventHorizonColor)
            break

        trajectory_y = math.tan(angle) * (gravityObjs[0][0] - pos[0]) + pos[1]
        # check which side of our projected trajectory the black hole will be on
        deflect = deflectionValue[math.floor(pos[0])][math.floor(pos[1])]
        if (math.cos(angle) * abs(pos[0] - gravityObjs[0][0])) < 0:
            deflect *= -1
        if trajectory_y < gravityObjs[0][1]:
            angle += deflect
        else:
            angle -= deflect

        # sceneStates[angleStep].append(pix[(pos[0], pos[1])])

        if DEBUG_TRACER_PATHS:
            oldPos = [pos[0] * tracerScale, pos[1] * tracerScale]

        pos[0] += math.cos(angle)
        pos[1] += math.sin(angle)
        if (pos[0] >= sceneSize[0]) | (pos[1] >= sceneSize[1]) | (pos[0] < 0) | (pos[1] < 0):
            pathAlive = 0
        elif DEBUG_TRACER_PATHS and pathAlive:
            pathDraw.line([oldPos, [pos[0] * tracerScale, pos[1] * tracerScale]], pathColor, 1)

        # draw to output image and rendering window
        if (pos[0] < sceneSize[0]) and (pos[0] >= 0) and (pos[1] < sceneSize[1]) and (pos[1] >= 0):
            screen.set_at((cameraPt[0] + int(counter * math.cos(startAngle)), cameraPt[1] + int(counter * math.sin(startAngle))), pix[(pos[0], pos[1])])
            if DEBUG_TRACER_RAYS:
                pathDraw.point((math.floor(pos[0] * tracerScale), math.floor(pos[1] * tracerScale)), (0, 0, 255))

            if pix[(pos[0], pos[1])] != nodataBackgroundColor:
                draw.point((cameraPt[0] + int(counter * math.cos(startAngle)), cameraPt[1] + int(counter * math.sin(startAngle))), pix[(pos[0], pos[1])])
        counter += 1
    pygame.display.update()

# draw black circle on black hole
draw.circle([gravityObjs[0][0], gravityObjs[0][1]], eventHorizon, (0,0,0), (255, 0, 0), 1)
if DEBUG_TRACER:
    pathDraw.circle([gravityObjs[0][0] * tracerScale, gravityObjs[0][1] * tracerScale], eventHorizon * tracerScale, (0,0,0), (0, 255, 255), 1)
# draw green circle on camera
draw.circle(cameraPt, 2, nodataBackgroundColor, (0,255,0), 1)
output.save(renderPath)

if DEBUG_TRACER:
    pathTrace.convert("RGB").save(tracerPath)
    pathTrace.close()
running = True
while running:
    # Handling input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()

pygame.quit()
scene.close()
output.close()
