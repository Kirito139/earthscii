"""Display a 3D map in a terminal window."""
import curses
import time
import argparse
import numpy as np
from earthscii.projection import project_map
from earthscii.renderer import render_map
from earthscii.map_loader import load_dem_as_points
from earthscii.globe_projection import project_globe
from earthscii.globe_tile_manager import load_visible_globe_points
from earthscii.globe_tile_manager import vector_from_latlon
from earthscii.utils import log


def main_wrapper():
    """Entry point for pip-installed script"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("tile", nargs="?", help="Path to a local tile")
    parser.add_argument("--globe", action="store_true", help="Enable global view")
    parser.add_argument("--lat", type=float, help="Initial latitude")
    parser.add_argument("--lon", type=float, help="Initial longitude")
    parser.add_argument( "--aspect", type=float, default=None, help="Override aspect ratio")

    args = parser.parse_args()

    curses.wrapper(lambda stdscr: main(stdscr, args))


def main(stdscr, args):
    log("[\033[32mINFO\033[0m] New session started\n------------")
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)
    stdscr.keypad(True)
    curses.start_color()

    # Define color pairs (foreground, background)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    is_global = args.globe

    angle_x = 0
    angle_y = 90
    angle_z = 0
    zoom = 0.8
    height, width = stdscr.getmaxyx()
    aspect_ratio = args.aspect if args.aspect is not None else min(height /
                                                                   width, 0.4)

    if is_global:
        if args.lat is not None and args.lon is not None:
            forward_vec = np.array(vector_from_latlon(args.lat, args.lon))

            # Derive angles from vector
            angle_x = int(np.degrees(np.arcsin(forward_vec[1])))  # pitch from y
            angle_y = int(np.degrees(np.arctan2(
                forward_vec[2],
                forward_vec[0]
            )))  # yaw from z/x
        else:
            fx = np.cos(np.radians(angle_y)) * np.cos(np.radians(angle_x))
            fy = np.sin(np.radians(angle_x))
            fz = np.sin(np.radians(angle_y)) * np.cos(np.radians(angle_x))
            forward_vec = np.array([fx, fy, fz])

            log(f"[\033[92mDEBUG\033[0m] forward_vec = {forward_vec}")
            log(f"[\033[92mDEBUG\033[0m] zoom = {zoom}, screen = {width}x{height}")

        globe_points = load_visible_globe_points(
            forward_vec, zoom, width, height, aspect_ratio
        )

    else:
        if not args.tile:
            raise ValueError("Local tile path must be provided when not using --globe")
        map_data, transform = load_dem_as_points(args.tile)

    offset_x, offset_y = width // 2, height // 2
    prev_state = None

    buffer = curses.newwin(height, width, 0, 0)

    while True:
        try:
            key = stdscr.getch()

            changed = False
            if key == ord('q'):
                log("[\033[32mINFO\033[0m] Exiting\n------------")
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
            elif key == ord('r'):
                angle_x, angle_y, angle_z = 0, 90, 0
                changed = True

            if changed:
                angle_x = max(min(angle_x, 89), -89)  # limit to +/- 89 degrees
                stdscr.refresh()

            if is_global and changed:
                forward_vec = np.array([
                    np.cos(np.radians(angle_y)) * np.cos(np.radians(angle_x)),
                    np.sin(np.radians(angle_x)),
                    np.sin(np.radians(angle_y)) * np.cos(np.radians(angle_x))
                ])
                globe_points = load_visible_globe_points(
                    forward_vec, zoom, width, height, aspect_ratio
                )

            state = (angle_x, angle_y, angle_z, zoom, offset_x, offset_y)

            if state != prev_state:
                buffer.erase()

                if is_global:
                    log(f"[\033[92mDEBUG\033[0m] angle_x = {angle_x}, angle_y = {angle_y}, angle_z = {angle_z}")
                    projected = project_globe(
                        globe_points,
                        angle_x, angle_y, angle_z,
                        zoom, offset_x, offset_y,
                        aspect_ratio=aspect_ratio
                    )

                else:
                    projected = project_map(
                        map_data,
                        angle_x, angle_y, angle_z,
                        zoom, offset_x, offset_y
                    )

                render_map(buffer, projected)

                if not is_global:
                    # display lat/lon of center
                    try:
                        from rasterio.transform import xy
                        # multiply by stride
                        lon, lat = xy(transform, (height // 2) * 16,
                                      (width // 2) * 16)
                        buffer.addstr(0, 1,
                                      f"Lat: {lat: .4f}, Lon: {lon: .4f}")
                    except:
                        pass

                elif is_global:
                    from globe_tile_manager import latlon_from_vector
                    lat, lon = latlon_from_vector(forward_vec)
                    buffer.addstr(0, 1, f"Lat: {lat: .4f}, Lon: {lon: .4f}")

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
    try:
        curses.wrapper(main)
    except Exception as e:
        import traceback
        with open("debug.log", "a") as f:
            f.write(f"{datetime.datetime.now()} |[\033[91mFATAL\033[0m] Uncaught Exception: {e}\n")
            traceback.print_exc(file=f)
        raise
