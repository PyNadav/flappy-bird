"""Scène démo « Et si toutes les voitures s'arrêtaient en même temps ? »"""
import bpy
import math
import os
import random

random.seed(7)

FPS = 30
TOTAL_FRAMES = 300
STOP_START = 150
STOP_LEN = 18

OUT = os.path.abspath(os.environ.get("OUT", "frames"))
PART = int(os.environ.get("PART", "0"))
PARTS = int(os.environ.get("PARTS", "1"))
PREVIEW = os.environ.get("PREVIEW") == "1"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 8 if PREVIEW else 32
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4
scene.render.use_persistent_data = True
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 50 if PREVIEW else 100
scene.render.fps = FPS
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(OUT, "f_")
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"


def mat(name, rgb, emit=0.0, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


M = {
    "asphalt": mat("asphalt", (0.025, 0.028, 0.04), rough=0.85),
    "sidewalk": mat("sidewalk", (0.09, 0.09, 0.12)),
    "line": mat("line", (1.0, 0.75, 0.1), emit=1.5),
    "building": mat("building", (0.05, 0.06, 0.13)),
    "building2": mat("building2", (0.08, 0.07, 0.15)),
    "win_warm": mat("win_warm", (1.0, 0.62, 0.25), emit=6),
    "win_cold": mat("win_cold", (0.55, 0.75, 1.0), emit=4),
    "glass": mat("glass", (0.02, 0.03, 0.05), rough=0.1),
    "headlight": mat("headlight", (1.0, 0.95, 0.8), emit=20),
    "taillight": mat("taillight", (1.0, 0.05, 0.03), emit=12),
    "tire": mat("tire", (0.01, 0.01, 0.01)),
}
CAR_COLORS = [
    (0.8, 0.12, 0.08), (0.95, 0.65, 0.05), (0.1, 0.35, 0.9), (0.9, 0.9, 0.92),
    (0.05, 0.05, 0.06), (0.15, 0.6, 0.3), (0.85, 0.35, 0.05),
]
CAR_MATS = [mat(f"car{i}", c, rough=0.3) for i, c in enumerate(CAR_COLORS)]

_meshes = {}


def cube_mesh(m):
    if m.name not in _meshes:
        me = bpy.data.meshes.new("cube_" + m.name)
        v = [(x, y, z) for x in (-.5, .5) for y in (-.5, .5) for z in (-.5, .5)]
        f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        me.from_pydata(v, [], f)
        me.update()
        me.materials.append(m)
        _meshes[m.name] = me
    return _meshes[m.name]


def box(loc, size, m, parent=None):
    o = bpy.data.objects.new("box", cube_mesh(m))
    o.location = loc
    o.scale = size
    scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    return o


ROAD_HALF = 7
Y_MIN, Y_MAX = -30, 220

box((0, (Y_MIN + Y_MAX) / 2, -0.1), (200, Y_MAX - Y_MIN + 100, 0.2), M["asphalt"])
for side in (-1, 1):
    box((side * (ROAD_HALF + 1), (Y_MIN + Y_MAX) / 2, 0.1),
        (2, Y_MAX - Y_MIN, 0.2), M["sidewalk"])

for y in range(Y_MIN, Y_MAX, 6):
    for x in (-3, 3):
        box((x, y, 0.01), (0.18, 2.5, 0.02), M["line"])
box((0, (Y_MIN + Y_MAX) / 2, 0.01), (0.25, Y_MAX - Y_MIN, 0.02), M["line"])

for side in (-1, 1):
    y = Y_MIN
    while y < Y_MAX:
        w = random.choice([6, 8, 10, 12])
        h = random.choice([12, 15, 18, 21, 24, 30, 36])
        d = 10
        x = side * (ROAD_HALF + 2 + d / 2)
        box((x, y + w / 2, h / 2), (d, w - 0.4, h),
            random.choice([M["building"], M["building2"]]))
        face_x = side * (ROAD_HALF + 2) - side * 0.02
        for wz in range(2, int(h) - 1, 3):
            for wy in range(1, int(w) - 1, 2):
                r = random.random()
                if r < 0.45:
                    wm = M["win_warm"]
                elif r < 0.6:
                    wm = M["win_cold"]
                else:
                    wm = M["glass"]
                box((face_x, y + wy + 0.5, wz + 0.8), (0.1, 1.1, 1.4), wm)
        y += w

for y in range(Y_MIN, Y_MAX, 18):
    for side in (-1, 1):
        ld = bpy.data.lights.new("lamp", "POINT")
        ld.energy = 900
        ld.color = (1.0, 0.7, 0.4)
        ld.shadow_soft_size = 0.5
        lo = bpy.data.objects.new("lamp", ld)
        lo.location = (side * (ROAD_HALF + 0.5), y, 7)
        scene.collection.objects.link(lo)

LANES = [(-5, -1), (-1.5, -1), (1.5, 1), (5, 1)]


def car_y(y0, v, f):
    if f <= STOP_START:
        return y0 + v * f
    t = min(f - STOP_START, STOP_LEN)
    return y0 + v * STOP_START + v * (t - t * t / (2 * STOP_LEN))


cars = 0
for lx, sens in LANES:
    y = Y_MIN - 40 if sens > 0 else Y_MIN + 10
    while y < Y_MAX + 40:
        y += random.uniform(9, 16)
        v = sens * random.uniform(0.32, 0.45)
        y0 = y - (v * STOP_START * 0.5)
        body = box((lx, y0, 0.75), (2.0, 4.2, 1.0), random.choice(CAR_MATS))
        box((0, -0.05, 0.85), (0.92, 0.55, 0.8), M["glass"], parent=body)
        for hx in (-0.32, 0.32):
            box((hx, sens * 0.505, 0.0), (0.18, 0.02, 0.18),
                M["headlight"], parent=body)
            box((hx, -sens * 0.505, 0.05), (0.2, 0.02, 0.12),
                M["taillight"], parent=body)
        for wx in (-0.5, 0.5):
            for wy in (-0.3, 0.3):
                box((wx, wy, -0.45), (0.12, 0.17, 0.5), M["tire"], parent=body)
        for f in range(1, TOTAL_FRAMES + 1, 2):
            body.location.y = car_y(y0, v, f)
            body.keyframe_insert("location", index=1, frame=f)
        cars += 1
print(f"[demo] {cars} voitures")

world = bpy.data.worlds.new("night")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.01, 0.015, 0.05, 1)
bg.inputs["Strength"].default_value = 1.0
scene.world = world

moon = bpy.data.lights.new("moon", "SUN")
moon.energy = 0.6
moon.color = (0.6, 0.7, 1.0)
mo = bpy.data.objects.new("moon", moon)
mo.rotation_euler = (math.radians(55), 0, math.radians(30))
scene.collection.objects.link(mo)

target = bpy.data.objects.new("target", None)
scene.collection.objects.link(target)
cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 24
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
c = cam.constraints.new("TRACK_TO")
c.target = target
c.track_axis = "TRACK_NEGATIVE_Z"
c.up_axis = "UP_Y"


def key(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert("location", frame=frame)


key(cam, 1, (0, -25, 45))
key(target, 1, (0, 60, 0))
key(cam, STOP_START, (0, 10, 16))
key(target, STOP_START, (0, 45, 2))
key(cam, TOTAL_FRAMES, (3, 18, 9))
key(target, TOTAL_FRAMES, (0, 40, 1.5))

per = math.ceil(TOTAL_FRAMES / PARTS)
scene.frame_start = 1 + PART * per
scene.frame_end = min(TOTAL_FRAMES, (PART + 1) * per)
print(f"[demo] rendu images {scene.frame_start}-{scene.frame_end} -> {OUT}")
os.makedirs(OUT, exist_ok=True)
bpy.ops.render.render(animation=True)
