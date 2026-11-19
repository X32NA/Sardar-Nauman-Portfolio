# Sardar Nauman Ahmed Maan · Mechanical portfolio

- [Design and drafting](https://x32na.github.io/Sardar-Nauman-Portfolio/design/)
- [FEA, CFD and thermal analysis](https://x32na.github.io/Sardar-Nauman-Portfolio/analysis/)

This is a static GitHub Pages site. The `design/` and `analysis/` pages are standalone links. Earlier project URLs redirect to their corresponding case studies.

The `work/` directory contains the VT-100 tray, SM-100 sensor stand, DF-200 drill fixture, and HX-200 cooling loop files. An assembled STEP, two millimetre-scale flat DXFs, and a three-sheet PDF are included for VT-100. Its CAD and DXF geometry can be regenerated with `python tools/generate_cad.py` (CadQuery and ezdxf). Run `python tools/generate_drawings.py` (also requires ReportLab) for the two PDFs. Build the SM-100 and DF-200 STEP, DXF, and render files with `python tools/generate_shop_projects.py` (also requires NumPy and Pillow), and their drawing sets with `python tools/draw_shop_projects.py`. The SolidWorks video and ANSYS screenshots in `images/` are evidence from earlier projects.

For a local preview, serve the repository root and open either portfolio path.
