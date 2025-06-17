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

    map_data, transform = load_dem_as_points("data/n37_w123_1arc_v3.tif")

    angle = 0
    zoom = 1.0
    height, width = stdscr.getmaxyx()
    offset_x, offset_y = width // 2, height // 2
    prev_state = None

    buffer = curses.newwin(height, width, 0, 0)
    buffer.border(
        curses.ACS_VLINE, curses.ACS_VLINE,  # Left and right borders
        curses.ACS_HLINE, curses.ACS_HLINE,  # Top and bottom borders
        curses.ACS_ULCORNER, curses.ACS_URCORNER,  # Corners
        curses.ACS_LLCORNER, curses.ACS_LRCORNER
    )

    while True:
        try:
            key = stdscr.getch()

            changed = False
            if key in (ord('q'), 3, 24):  # q, ctrl-c, ctrl-x
                break
            elif key == curses.KEY_LEFT:
                angle -= 2
                changed = True
            elif key == curses.KEY_RIGHT:
                angle += 2
                changed = True
            elif key == ord('+') or key == ord('='):
                zoom *= 1.1
                changed = True
            elif key == ord('-') or key == ord('_'):
                zoom /= 1.1
                changed = True
            elif key in (ord('w'), ord('W')):
                offset_y += 2
                changed = True
            elif key in (ord('s'), ord('S')):
                offset_y -= 2
                changed = True
            elif key in (ord('a'), ord('A')):
                offset_x += 2
                changed = True
            elif key in (ord('d'), ord('D')):
                offset_x -= 2
                changed = True

            state = (angle, zoom, offset_x, offset_y)

            if state != prev_state:
                buffer.erase()

                projected = project_map(map_data, angle, zoom, offset_x, offset_y)
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
            buffer.addstr(0, 50, "▲ = high", curses.color_pair(3))
            buffer.addstr(1, 50, "~ = low", curses.color_pair(1))


            buffer.noutrefresh()
            curses.doupdate()
            prev_state = state


        except KeyboardInterrupt:
            break

        time.sleep(0.016)


if __name__ == '__main__':
    curses.wrapper(main)
