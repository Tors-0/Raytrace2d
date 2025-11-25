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

cameraPt = [48, 75]
gravityObjs = [[159, 65, 5], [132,  904, 0.1]]
sceneSize = scene.size
vecField = [[(0,0)]]
for x in range(sceneSize[0]):
    for y in range(sceneSize[1]):
        pass