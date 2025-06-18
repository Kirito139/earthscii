"""Display a 3D map in a terminal window."""
import curses
import time
from projection import project_map
from renderer import render_map
from map_loader import load_dem_as_points


def main(stdscr):
    """Main loop."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)
    stdscr.keypad(True)
    curses.start_color()

    # Define color pairs (foreground, background)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    map_data, transform = load_dem_as_points(
        "/home/lmulder/earthscii/data/n37_w123_1arc_v3.tif")

    angle_x = 0
    angle_y = 0
    angle_z = 0
    zoom = 1.0
    height, width = stdscr.getmaxyx()
    offset_x, offset_y = width // 2, height // 2
    prev_state = None

    buffer = curses.newwin(height, width, 0, 0)

    while True:
        try:
            key = stdscr.getch()

            changed = False
            if key in (ord('q'), 3, 24):  # q, ctrl-c, ctrl-x
                break
            elif key == ord('w'):  # tilt up
                angle_x -= 5
                changed = True
            elif key == ord('s'):  # tilt down
                angle_x += 5
                changed = True
            elif key == ord('a'):  # rotate left (yaw)
                angle_z -= 5
                changed = True
            elif key == ord('d'):  # rotate right (yaw)
                angle_z += 5
                changed = True
            elif key == ord(','):
                angle_y -= 5  # orbit left
                changed = True
            elif key == ord('.'):
                angle_y += 5  # orbit right
                changed = True
            elif key == ord('+') or key == ord('='):
                zoom *= 1.1
                changed = True
            elif key == ord('-'):
                zoom /= 1.1
                changed = True
            elif key == curses.KEY_UP:
                offset_y -= 1
                changed = True
            elif key == curses.KEY_DOWN:
                offset_y += 1
                changed = True
            elif key == curses.KEY_LEFT:
                offset_x -= 1
                changed = True
            elif key == curses.KEY_RIGHT:
                offset_x += 1
                changed = True

            if changed:
                stdscr.refresh()

            state = (angle_x, angle_y, angle_z, zoom, offset_x, offset_y)

            if state != prev_state:
                buffer.erase()

                projected = project_map(map_data, angle_x, angle_y, angle_z,
                                        zoom, offset_x, offset_y)
                render_map(buffer, projected)

                # display lat/lon of center
                try:
                    from rasterio.transform import xy
                    # multiply by stride
                    lon, lat = xy(transform, (height // 2) * 16, (width // 2) * 16)
                    buffer.addstr(0, 1, f"Lat: {lat: .4f}, Lon: {lon: .4f}")
                except:
                    pass

            buffer.addstr(0, 0, "@")  # This should always appear in top-left
            buffer.addstr(0, 50, f"angle_x = {angle_x}", curses.color_pair(3))
            buffer.addstr(1, 50, f"angle_y = {angle_y}", curses.color_pair(3))
            buffer.addstr(2, 50, f"angle_z = {angle_z}", curses.color_pair(3))

            buffer.noutrefresh()
            curses.doupdate()
            prev_state = state

        except KeyboardInterrupt:
            break

        time.sleep(0.016)


if __name__ == '__main__':
    curses.wrapper(main)
