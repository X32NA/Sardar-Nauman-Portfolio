"""Build the sensor stand and drill locating fixture CAD files."""
from pathlib import Path

import cadquery as cq
import ezdxf
from ezdxf import units
import numpy as np
from PIL import Image

from generate_cad import TRAY_HOLES, bracket, nut, screw, tray

OUT = Path(__file__).resolve().parents[1] / "work"
BASE = "#92aebb"
MOUNT = "#559b9e"
CARRIAGE = "#e39b5d"
HARDWARE = "#b3c5cd"


def block(x, y, z, dx, dy, dz):
    return cq.Workplane("XY", origin=(x, y, z)).box(dx, dy, dz, centered=False).val()


def holes_xy(shape, points, dia, z, depth):
    tool = cq.Workplane("XY", origin=(0, 0, z)).pushPoints(points).circle(dia/2).extrude(depth)
    return shape.cut(tool.val())


def holes_y(shape, points, dia, y, depth):
    xz = cq.Plane(origin=(0, y, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    tool = cq.Workplane(xz).pushPoints(points).circle(dia/2).extrude(depth)
    return shape.cut(tool.val())


def cylinder(dia, length, origin, direction=(0, 0, 1)):
    return cq.Solid.makeCylinder(dia/2, length, origin, direction)


STAND_ANCHORS = [(x, y) for x in (12, 88) for y in (12, 58)]
POST_FASTENERS = [(44, 51), (56, 51)]
FIXTURE_ANCHORS = [(x, y) for x in (10, 125) for y in (10, 80)]
FIXTURE_PINS = [(42, 20), (90, 20), (24, 43)]
GUIDE_FASTENERS = [(56, 70), (76, 70)]
DRILL_AXIS = (66, 43)


def sensor_parts():
    base = holes_xy(block(0, 0, 0, 100, 70, 10), STAND_ANCHORS, 6.6, -1, 12)
    base = holes_xy(base, POST_FASTENERS, 4.5, -1, 12)
    base = holes_xy(base, POST_FASTENERS, 8, -1, 5.4)
    plate = holes_xy(block(38, 46, 10, 24, 10, 120), POST_FASTENERS, 3.3, 9, 11)
    slot_plane = cq.Plane(origin=(0, 57, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    cut = cq.Workplane(slot_plane).center(50, 78).slot2D(60, 6.6, 90).extrude(12).val()
    plate = plate.cut(cut)
    carriage = holes_y(block(32, 30, 56, 36, 16, 44), [(50, 68), (50, 88)], 5, 47, 8)
    carriage = carriage.cut(cylinder(12.2, 38, (31, 38, 78), (1, 0, 0)))
    sensor = cylinder(12, 64, (14, 38, 78), (1, 0, 0))
    return [("Machined base", base, BASE), ("Slotted upright", plate, MOUNT),
            ("Sensor carriage", carriage, CARRIAGE), ("M12 sensor envelope", sensor, HARDWARE)]


def fixture_parts():
    base = holes_xy(block(0, 0, 0, 135, 90, 12), FIXTURE_ANCHORS, 6.6, -1, 14)
    base = holes_xy(base, FIXTURE_PINS, 6, -1, 14)
    base = holes_xy(base, GUIDE_FASTENERS, 4.2, -1, 14)
    base = holes_xy(base, [DRILL_AXIS], 10, -1, 14)
    guide = block(49, 33, 18, 34, 43, 14).fuse(block(49, 64, 12, 34, 12, 6)).clean()
    guide = holes_xy(guide, [DRILL_AXIS], 12, 17, 16)
    guide = holes_xy(guide, GUIDE_FASTENERS, 5.5, 11, 22)
    bush = cylinder(12, 14, (66, 43, 18)).fuse(cylinder(16, 2, (66, 43, 32)))
    bush = bush.cut(cylinder(6.05, 18, (66, 43, 17))).clean()
    pins = [(f"Locator pin {i}", cylinder(6, 18, (x, y, 0)), HARDWARE)
            for i, (x, y) in enumerate(FIXTURE_PINS, 1)]
    return [("Fixture base", base, BASE), ("Stepped guide block", guide, MOUNT),
            ("Shouldered drill bushing", bush, CARRIAGE), *pins]


def check_and_export(name, parts):
    model = cq.Assembly(name=name)
    for i, (label, part, color) in enumerate(parts):
        assert part.isValid() and len(part.Solids()) == 1, label
        for other_label, other, _ in parts[:i]:
            overlap = part.intersect(other)
            assert not overlap.Solids() or overlap.Volume() < 1e-5, (label, other_label)
        color_values = [int(color[j:j+2], 16)/255 for j in (1, 3, 5)]
        model.add(part, name=label, color=cq.Color(*color_values))
    path = OUT / (name + ".step")
    model.export(str(path), write_pcurves=False)
    restored = cq.importers.importStep(str(path)).val()
    assert len(restored.Solids()) == len(parts) and restored.isValid(), name
    print(name, f"{len(parts)} valid solids, no nominal interference")


def profile(name, width, height, cutouts):
    doc = ezdxf.new("R2010", units=units.MM)
    doc.header["$MEASUREMENT"] = 1
    for layer, color in [("OUTLINE", 7), ("DRILL", 3), ("TAP_DRILL", 6), ("COUNTERBORE_BACK", 4)]:
        doc.layers.new(layer, dxfattribs={"color": color})
    space = doc.modelspace()
    space.add_lwpolyline([(0, 0), (width, 0), (width, height), (0, height)], close=True,
                         dxfattribs={"layer": "OUTLINE"})
    for layer, points, diameter in cutouts:
        for point in points:
            space.add_circle(point, diameter/2, dxfattribs={"layer": layer})
    doc.saveas(OUT / (name + ".dxf"))
    assert not ezdxf.readfile(OUT / (name + ".dxf")).audit().errors


def cad_render(name, parts, azimuth, elevation):
    w, h = 1100, 760
    c, s = np.cos(azimuth), np.sin(azimuth)
    ce, se = np.cos(elevation), np.sin(elevation)
    rendered = []
    for _, part, color in parts:
        points, faces = part.tessellate(.25, .24)
        x, y, z = np.asarray([p.toTuple() for p in points]).T
        u, v = c*x - s*y, s*x + c*y
        p = np.column_stack((u, ce*z + se*v, se*z - ce*v))
        rgb = np.array([int(color[j:j+2], 16) for j in (1, 3, 5)])
        rendered.append((p, faces, rgb))
    cloud = np.vstack([p for p, _, _ in rendered])
    left, bottom = cloud.min(axis=0)[:2]
    right, top = cloud.max(axis=0)[:2]
    zoom = min((w-175)/(right-left), (h-140)/(top-bottom))
    yy, xx = np.mgrid[:h, :w]
    glow = np.clip(1 - np.hypot((xx-w*.48)/(w*.8), (yy-h*.36)/(h*.95)), 0, 1)
    pixels = np.array([12,35,45]) + glow[..., None] * np.array([21,33,38])
    pixels = pixels.astype(np.uint8)
    pixels[:, ::40] += 4
    pixels[::40, :] += 4
    depth = np.full((h, w), -np.inf)
    for points, faces, rgb in rendered:
        p = points.copy()
        p[:, 0] = w/2 + (p[:, 0] - (left+right)/2)*zoom
        p[:, 1] = h/2 - (p[:, 1] - (bottom+top)/2)*zoom
        for ids in faces:
            a, b, d = points[list(ids)]
            n = np.cross(b-a, d-a)
            if n[2] <= 1e-8:
                continue
            shade = np.clip(.71 + .32*np.dot(n, [-.36,.78,.5])/np.linalg.norm(n), .35, 1.08)
            a,b,d = p[list(ids)]
            x0,y0 = np.floor(np.min([a,b,d],axis=0)[:2]).astype(int)
            x1,y1 = np.ceil(np.max([a,b,d],axis=0)[:2]).astype(int)
            xe,ye = xx[y0:y1+1,x0:x1+1]+.5,yy[y0:y1+1,x0:x1+1]+.5
            den = (b[1]-d[1])*(a[0]-d[0]) + (d[0]-b[0])*(a[1]-d[1])
            u = ((b[1]-d[1])*(xe-d[0]) + (d[0]-b[0])*(ye-d[1]))/den
            v = ((d[1]-a[1])*(xe-d[0]) + (a[0]-d[0])*(ye-d[1]))/den
            t = 1-u-v
            zz = u*a[2] + v*b[2] + t*d[2]
            window = depth[y0:y1+1,x0:x1+1]
            mask = (u>=-1e-6) & (v>=-1e-6) & (t>=-1e-6) & (zz>window)
            window[mask] = zz[mask]
            pixels[y0:y1+1,x0:x1+1][mask] = np.minimum(rgb*shade,255)
    Image.fromarray(pixels).save(OUT / (name + ".webp"), quality=91)


def generate():
    sensor, fixture = sensor_parts(), fixture_parts()
    check_and_export("SM-100-sensor-stand", sensor)
    check_and_export("DF-200-drill-fixture", fixture)
    profile("SM-101-base-machining", 100, 70, [
        ("DRILL", STAND_ANCHORS, 6.6), ("DRILL", POST_FASTENERS, 4.5),
        ("COUNTERBORE_BACK", POST_FASTENERS, 8)])
    profile("DF-201-base-machining", 135, 90, [
        ("DRILL", FIXTURE_ANCHORS, 6.6), ("DRILL", [DRILL_AXIS], 10),
        ("DRILL", FIXTURE_PINS, 6), ("TAP_DRILL", GUIDE_FASTENERS, 4.2)])
    brackets = bracket()
    tray_parts = [("Tray", tray().translate((0, 0, 84)), BASE),
                  ("Left bracket", brackets.translate((30, 0, 0)), MOUNT),
                  ("Right bracket", brackets.translate((280, 0, 0)), MOUNT)]
    for x,y in TRAY_HOLES:
        tray_parts.append(("Screw",screw(x,y).translate((0,0,115)),CARRIAGE))
        tray_parts.append(("Nut",nut(x,y).translate((0,0,-26)),CARRIAGE))
    cad_render("tray-cover", tray_parts, -.57, .59)
    cad_render("sm-100-iso", sensor, -.63, .46)
    displaced = [(label, part.translate((0,0,17 if i == 2 else 7 if i == 1 else 0)), color)
                 for i,(label,part,color) in enumerate(fixture)]
    cad_render("df-200-iso", displaced, -.57, .65)


if __name__ == "__main__":
    generate()
