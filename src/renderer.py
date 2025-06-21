"""Map depth to ASCII and place chars."""
import curses

def render_map(buffer, projected_points):
    chars = ".,:-=+*#%@"
    if not projected_points:
        return

    height, width = buffer.getmaxyx()
    min_depth = min(p[2] for p in projected_points)
    max_depth = max(p[2] for p in projected_points)
    depth_range = max_depth - min_depth or 1

    for x, y, depth in projected_points:
        ix, iy = int(x), int(y)
        if 0 <= iy < height and 0 <= ix < width:
            norm = (depth - min_depth) / depth_range  # normalized depth
            ch = chars[int(norm * (len(chars) - 1))]

            # Assign color based on height
            if norm < 0.045:
                color = curses.color_pair(1)
            elif norm < 0.6:
                color = curses.color_pair(2)
            else:
                color = curses.color_pair(3)

            try:
                buffer.addch(iy, ix, ch, color)
            except:
                pass # silently ignore out-of-bounds
