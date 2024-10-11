#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import gmsh
geo = gmsh.model.geo

gmsh.initialize()
gmsh.model.add("CEPC_strip")

# bulk points
lc_up = 2e-5
lc_down = 2e-4
P1 = geo.addPoint(0, 0, 0, lc_up)
P2 = geo.addPoint(0, 75.5e-4, 0, lc_up)
P3 = geo.addPoint(150e-4, 75.5e-4, 0, lc_down)
P4 = geo.addPoint(150e-4, 0, 0, lc_down)

P17 = geo.addPoint(147e-4, 75.5e-4, 0, lc_down)
P18 = geo.addPoint(147e-4, 0, 0, lc_down)

# p stop 1
lp = 1e-5
# P1 = geo.addPoint(0, 0, 0, lc_up)
P6 = geo.addPoint(0, 1e-4, 0, lc_up)
P7 = geo.addPoint(-1e-4, 1e-4, 0, lp)
P8 = geo.addPoint(-1e-4, 0, 0, lp)

L1 = geo.addLine(P1, P8)
L2 = geo.addLine(P8, P7)
L3 = geo.addLine(P7, P6)
L15 = geo.addLine(P1, P6)

loop1 = geo.addCurveLoop([L1, L2, L3, -L15])
surf1 = geo.addPlaneSurface([loop1])

# p well 1
P19 = geo.addPoint(2e-4, 0, 0, lc_up)
P20 = geo.addPoint(2e-4, 1e-4, 0, lc_up)
# P1 = geo.addPoint(0, 0, 0, lc_up)
# P6 = geo.addPoint(0, 1e-4, 0, lc_up)

L21 = geo.addLine(P1, P19)
L22 = geo.addLine(P19, P20)
L23 = geo.addLine(P20, P6)
# L15 = geo.addLine(P1, P6)

loop2 = geo.addCurveLoop([L21, L22, L23, -L15])
surf2 = geo.addPlaneSurface([loop2])

# p stop 2
P9 = geo.addPoint(0,74.5e-4, 0, lc_up)
# P2 = geo.addPoint(0,75.5e-4, 0, lc_up)
P11 = geo.addPoint(-1e-4,75.5e-4, 0, lp)
P12 = geo.addPoint(-1e-4,74.5e-4, 0, lp)

L9 = geo.addLine(P9, P12)
L10 = geo.addLine(P12, P11)
L11 = geo.addLine(P11, P2)
L17 = geo.addLine(P9, P2)

loop3 = geo.addCurveLoop([L9, L10, L11, -L17])
surf3 = geo.addPlaneSurface([loop3])

# p well 2

P21 = geo.addPoint(2e-4,75.5e-4, 0, lc_up)
P22 = geo.addPoint(2e-4,74.5e-4, 0, lc_up)
# P9 = geo.addPoint(0,74.5e-4, 0, lc_up)
# P2 = geo.addPoint(0,75.5e-4, 0, lc_up)

L24 = geo.addLine(P2, P21)
L25 = geo.addLine(P21, P22)
L26 = geo.addLine(P22, P9)
# L17 = geo.addLine(P9, P2)

loop4 = geo.addCurveLoop([L24, L25, L26, L17])
surf4 = geo.addPlaneSurface([loop4])

# n stop
ln = 1e-5
P13 = geo.addPoint(0, 30.25e-4, 0, lc_up)
P14 = geo.addPoint(0, 45.25e-4, 0, lc_up)
P23 = geo.addPoint(-0.5e-4, 45.25e-4, 0, lc_up)
P24 = geo.addPoint(-0.5e-4, 30.25e-4, 0, lc_up)
P15 = geo.addPoint(-1e-4, 45.25e-4, 0, ln)
P16 = geo.addPoint(-1e-4, 30.25e-4, 0, ln)

L27 = geo.addLine(P15, P23)
L28 = geo.addLine(P23, P24)
L29 = geo.addLine(P24, P16)
L6 = geo.addLine(P16, P15)

loop5 = geo.addCurveLoop([L27, L28, L29, L6])
surf5 = geo.addPlaneSurface([loop5])

L5 = geo.addLine(P23, P14)
L35 = geo.addLine(P13, P14)
L7 = geo.addLine(P13, P24)
# L28 = geo.addLine(P23, P24)

loop6 = geo.addCurveLoop([L5, -L35, L7, -L28])
surf6 = geo.addPlaneSurface([loop6])

# n well
P25 = geo.addPoint(2e-4, 46.75e-4, 0, lc_up)
P26 = geo.addPoint(2e-4, 28.75e-4, 0, lc_up)
P27 = geo.addPoint(0e-4, 46.75e-4, 0, lc_up)
P28 = geo.addPoint(0e-4, 28.75e-4, 0, lc_up)
# P13 = geo.addPoint(0, 30.25e-4, 0, lc_up)
# P14 = geo.addPoint(0, 45.25e-4, 0, lc_up)

L30 = geo.addLine(P28, P26)
L31 = geo.addLine(P26, P25)
L32 = geo.addLine(P25, P27)
L33 = geo.addLine(P27, P14)
L34 = geo.addLine(P13, P28)
# L35 = geo.addLine(P13, P14)

loop7 = geo.addCurveLoop([L30, L31, L32, L33, -L35, L34])
surf7 = geo.addPlaneSurface([loop7])

# bulk lines & surfaces

# L22 = geo.addLine(P19, P20)
# L23 = geo.addLine(P20, P6)
L4 = geo.addLine(P6, P28)
# L30 = geo.addLine(P28, P26)
# L31 = geo.addLine(P26, P25)
# L32 = geo.addLine(P25, P27)
L36 = geo.addLine(P27, P9)
# L26 = geo.addLine(P22, P9)
# L25 = geo.addLine(P21, P22)
L12 = geo.addLine(P21, P17)
L13 = geo.addLine(P17, P18)
L14 = geo.addLine(P18, P19)

loop8 = geo.addCurveLoop([L22, L23, L4, L30, L31, L32, L36, -L26, -L25, L12, L13, L14])
surf8 = geo.addPlaneSurface([loop8])

L18 = geo.addLine(P17, P3)
L19 = geo.addLine(P3, P4)
L20 = geo.addLine(P4, P18)
# L13 = geo.addLine(P17, P18)

loop9 = geo.addCurveLoop([L18, L19, L20, -L13])
surf9 = geo.addPlaneSurface([loop9])

geo.synchronize()

gmsh.model.addPhysicalGroup(1, [L19], name="bot")
gmsh.model.addPhysicalGroup(1, [L6], name="top")

gmsh.model.addPhysicalGroup(2, [surf1, surf2, surf3, surf4, surf5, surf6, surf7, surf8, surf9], name="CEPC_strip")

gmsh.option.setNumber("Geometry.MatchMeshTolerance", 1e-12)
gmsh.model.mesh.generate(2)

gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write("./param_file/temp_mesh/CEPC_strip.msh")
gmsh.finalize()
# gmsh.fltk.run()
