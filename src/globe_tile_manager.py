import math
import requests
from pathlib import Path
from etopo_loader import load_etopo_as_sphere_points
import datetime

def log(msg):
    """Log a message to debug.log."""
    with open("debug.log", "a") as f:
        f.write(f"{datetime.datetime.now()} | {msg}\n")


TILE_DIR = Path("./tiles")
TILE_DIR.mkdir(parents=True, exist_ok=True)
PARTIAL_SUFFIX = ".partial"

def estimate_fov_from_screen(forward_vec, zoom, screen_width, screen_height):
    """
    Estimate the angular field of view in degrees covered by the screen.
    """
    EARTH_RADIUS = 6371000  # meters
    ASPECT_RATIO = 0.5  # same as in projection
    screen_width_m = screen_width / zoom
    screen_height_m = screen_height / (zoom * ASPECT_RATIO)

    # Convert visible width on screen (in meters) into angle at Earth's surface
    angular_width_deg = math.degrees(screen_width_m / EARTH_RADIUS)
    angular_height_deg = math.degrees(screen_height_m / EARTH_RADIUS)
    return angular_width_deg, angular_height_deg


def etopo2022_filename(lat, lon):
    ns = 'N' if lat >= 0 else 'S'
    ew = 'E' if lon >= 0 else 'W'
    return f"ETOPO_2022_v1_15s_{ns}{abs(lat):02d}{ew}{abs(lon):03d}_surface.tif"


def download_etopo2022_tile(lat, lon):
    fname = etopo2022_filename(lat, lon)
    local_path = TILE_DIR / fname
    partial_path = local_path.with_suffix(local_path.suffix + PARTIAL_SUFFIX)

    if local_path.exists():
        return str(local_path)
    if partial_path.exists():
        print(f"Removing incomplete download: {partial_path}")
        partial_path.unlink()

    base_url = "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/"
    url = base_url + fname
    print(f"Downloading {fname}...")
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(partial_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            partial_path.rename(local_path)
            return str(local_path)
        else:
            print(f"Failed to fetch: {url} ({r.status_code})")
    except Exception as e:
        print(f"Error: {e}")
        if partial_path.exists():
            partial_path.unlink()
    return None


def latlon_from_vector(v):
    x, y, z = v
    lat = math.degrees(math.asin(z / math.sqrt(x*x + y*y + z*z)))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon

def vector_from_latlon(lat, lon):
    """Converts geographic coordinates to a 3D unit vector."""
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = math.cos(lat_rad) * math.cos(lon_rad)
    y = math.cos(lat_rad) * math.sin(lon_rad)
    z = math.sin(lat_rad)
    return x, y, z



def align_to_15(x):
    """Round x to the nearest multiple of 15."""
    return int(round(x / 15)) * 15


def get_visible_tile_coords(forward_vec, fov_degrees, padding):
    lat_center, lon_center = latlon_from_vector(forward_vec)
    lat_min = int(lat_center - fov_degrees // 2) - padding
    lat_max = int(lat_center + fov_degrees // 2) + padding
    lon_min = int(lon_center - fov_degrees // 2) - padding
    lon_max = int(lon_center + fov_degrees // 2) + padding
    lat_min = max(-85, lat_min)
    lat_max = min(85, lat_max)

    lat_min_aligned = align_to_15(lat_min)
    lat_max_aligned = align_to_15(lat_max)
    lon_min_aligned = align_to_15(lon_min)
    lon_max_aligned = align_to_15(lon_max)

    return [
        (lat, lon)
        for lat in range(lat_min_aligned, lat_max_aligned + 1, 15)
        for lon in range(lon_min_aligned, lon_max_aligned + 1, 15)
    ]


def load_visible_globe_points(forward_vec, zoom, screen_width, screen_height):
    fov_horiz, fov_vert = estimate_fov_from_screen(forward_vec, zoom,
                                                   screen_width, screen_height)
    tile_coords = get_visible_tile_coords(forward_vec, fov_degrees=fov_horiz,
                                          padding=1)
    paths = []
    for lat, lon in tile_coords:
        path = download_etopo2022_tile(lat, lon)
        log(f"[INFO] Downloading tile: lat={lat}, lon={lon}")
        if path:
            paths.append(path)

    stride = compute_lod_stride(zoom)
    all_points = []
    for path in paths:
        points = load_etopo_as_sphere_points(path, stride=stride)
        all_points.extend(points)

    log(f"[DEBUG] Looking for tiles near: {latlon_from_vector(forward_vec)}")
    log(f"[DEBUG] Tile coords to load: {tile_coords}")
    log(f"[INFO] Loaded {len(paths)} tile(s)")
    log(f"[INFO] Loaded {len(all_points)} points")

    return all_points


def compute_lod_stride(zoom):
    log(f"[DEBUG] stride in use with zoom: {zoom}")
    if zoom > 3.0:
        return 2
    elif zoom > 2.0:
        return 4
    elif zoom > 1.0:
        return 8
    elif zoom > 0.5:
        return 16
    else:
        return 32
