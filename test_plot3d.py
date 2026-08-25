from sage.plot.plot3d.shapes import sphere

s = sphere()
png = s._repr_png_()
assert png is not None and png[:8] == b'\x89PNG\r\n\x1a\n'
print(f"Graphics3d OK - {len(png)} bytes")
