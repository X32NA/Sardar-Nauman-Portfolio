"""Generate the sheet-metal demonstration geometry, flat DXFs, and viewer data."""
from math import pi, sqrt
from pathlib import Path
import json

import cadquery as cq
import ezdxf
from ezdxf import units

OUT = Path(__file__).resolve().parents[1] / "work"
D = sqrt(0.5)
WIDTH = 360
TRAY_DEPTH = 160
TRAY_HOLES = [(x, y) for x in (55, 305) for y in (27, 127)]
K = 0.40
TRAY_BA = pi / 2 * (3 + K * 2)
BRACKET_BA = pi / 2 * (3 + K * 3)
TRAY_FLAT = 200 + 2 * TRAY_BA
BRACKET_FLAT = 218 + BRACKET_BA
YZ = cq.Plane(origin=(0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))


def tray():
    profile = (cq.Workplane(YZ).moveTo(0, 24).lineTo(0, 5)
               .threePointArc((5-5*D, 5-5*D), (5, 0)).lineTo(155, 0)
               .threePointArc((155+5*D, 5-5*D), (160, 5))
               .lineTo(160, 36).lineTo(158, 36).lineTo(158, 5)
               .threePointArc((155+3*D, 5-3*D), (155, 2)).lineTo(5, 2)
               .threePointArc((5-3*D, 5-3*D), (2, 5))
               .lineTo(2, 24).close().extrude(WIDTH))
    holes = cq.Workplane("XY", origin=(0, 0, -1)).pushPoints(TRAY_HOLES).circle(2.75).extrude(4)
    return profile.cut(holes).val()


def bracket():
    profile = (cq.Workplane(YZ).moveTo(6, 0).lineTo(163, 0)
               .threePointArc((163+3*D, 3-3*D), (166, 3))
               .lineTo(166, 64).lineTo(169, 64).lineTo(169, 3)
               .threePointArc((163+6*D, 3-6*D), (163, -3))
               .lineTo(6, -3).close().extrude(50))
    holes = cq.Workplane("XY", origin=(0, 0, -4)).pushPoints([(25, 27), (25, 127)]).circle(2.75).extrude(5)
    wall_plane = cq.Plane(origin=(0, 170, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    slots = cq.Workplane(wall_plane).pushPoints([(25, 24), (25, 48)]).slot2D(14, 7, 90).extrude(5)
    return profile.cut(holes).cut(slots).val()


def screw(x, y):
    stub = cq.Workplane("XY", origin=(x, y, -8)).circle(2.5).extrude(10)
    head = cq.Workplane("XY", origin=(x, y, 2)).polygon(6, 9.2).extrude(3)
    return stub.union(head).val()


def nut(x, y):
    return (cq.Workplane("XY", origin=(x, y, -7)).polygon(6, 9.2)
            .circle(2.55).extrude(4).val())


def flat_file(name, width, length, holes, folds, slots=()):
    doc = ezdxf.new("R2010", units=units.MM)
    doc.header["$MEASUREMENT"] = 1
    doc.layers.new("CUT", dxfattribs={"color": 7})
    doc.layers.new("BEND_CENTER", dxfattribs={"color": 4})
    msp = doc.modelspace()
    cut = {"layer": "CUT"}
    msp.add_lwpolyline([(0, 0), (width, 0), (width, length), (0, length)], close=True, dxfattribs=cut)
    for center in holes:
        msp.add_circle(center, 2.75, dxfattribs=cut)
    for center_x, center_y in slots:
        r = 3.5
        lower, upper = center_y - r, center_y + r
        msp.add_lwpolyline([(center_x+r, lower, 0), (center_x+r, upper, 1),
                            (center_x-r, upper, 0), (center_x-r, lower, 1)],
                           format="xyb", close=True, dxfattribs=cut)
    for fold in folds:
        msp.add_line((0, fold), (width, fold), dxfattribs={"layer": "BEND_CENTER"})
    assert not doc.audit().errors
    doc.saveas(OUT / name)


def generate():
    body, support = tray(), bracket()
    specs = [("Tray", body, "#a9c8da", 61),
             ("Left bracket", support.translate((30, 0, 0)), "#437b91", 0),
             ("Right bracket", support.translate((280, 0, 0)), "#437b91", 0)]
    for i, (x, y) in enumerate(TRAY_HOLES, 1):
        specs.append((f"M5 screw {i}", screw(x, y), "#e49d5b", 96))
        specs.append((f"M5 nut {i}", nut(x, y), "#e49d5b", -25))
    models = cq.Assembly(name="VT-100 Van Tray")
    for name, shape, colour, _ in specs:
        assert shape.isValid() and len(shape.Solids()) == 1, name
        rgb = [int(colour[i:i+2], 16) / 255 for i in (1, 3, 5)]
        models.add(shape, name=name, color=cq.Color(*rgb))
    for i, (name, part, _, _) in enumerate(specs):
        for other_name, other, _, _ in specs[:i]:
            overlap = part.intersect(other)
            assert not overlap.Solids() or abs(overlap.Volume()) < 1e-5, (name, other_name)
    models.export(str(OUT / "VT-100-tray-assembly.step"))
    exported = cq.importers.importStep(str(OUT / "VT-100-tray-assembly.step")).val()
    assert len(exported.Solids()) == len(specs)
    model = []
    for name, shape, color, lift in specs:
        vertices, triangles = shape.tessellate(0.30, 0.28)
        model.append({"name": name, "color": color, "lift": lift,
                      "vertices": [[round(c, 3) for c in v.toTuple()] for v in vertices],
                      "triangles": triangles})
    (OUT / "tray-mesh.js").write_text("window.trayMesh = " + json.dumps(model, separators=(",", ":")) + ";\n")
    flat_file("VT-101-tray-flat.dxf", WIDTH, TRAY_FLAT,
              [(x, 19 + TRAY_BA + y - 5) for x, y in TRAY_HOLES],
              [19 + TRAY_BA/2, 169 + 3*TRAY_BA/2])
    flat_file("VT-102-bracket-flat.dxf", 50, BRACKET_FLAT, [(25, 21), (25, 121)],
              [157 + BRACKET_BA/2], [(25, 157 + BRACKET_BA + z - 3) for z in (24, 48)])
    print(f"Verified {len(specs)} solids, zero interferences; flat lengths {TRAY_FLAT:.2f}, {BRACKET_FLAT:.2f} mm.")


if __name__ == "__main__":
    generate()
