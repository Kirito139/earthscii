import math
import numpy as np
import datetime

def log(msg):
    """Log a message to debug.log."""
    with open("debug.log", "a") as f:
        f.write(f"{datetime.datetime.now()} | {msg}\n")

def project_globe(points, angle_x=0, angle_y=0, angle_z=0, zoom=1.0, offset_x=0, offset_y=0):
    log(f"[INFO] Projecting {len(points)} points")
    projected = []
    ASPECT_RATIO = 0.5

    # Compute camera rotation
    ax = math.radians(angle_x)
    ay = math.radians(angle_y)
    az = math.radians(angle_z)

    # Camera forward vector
    fx = math.cos(ay) * math.cos(ax)
    fy = math.sin(ax)
    fz = math.sin(ay) * math.cos(ax)
    forward = np.array([fx, fy, fz])
    forward /= np.linalg.norm(forward)

    world_up = np.array([0, 1, 0])
    right = np.cross(world_up, forward)
    right /= np.linalg.norm(right)
    up = np.cross(forward, right)

    for p in points:
        rel = np.array(p)

        # Discard back-facing hemisphere
        if np.dot(forward, rel / np.linalg.norm(rel)) < 0:
            continue

        SCALE = 9e-6  # tweak this value to match your needs

        sx = int(np.dot(rel, right) * zoom * SCALE) + offset_x
        sy = int(np.dot(rel, up) * zoom * SCALE * ASPECT_RATIO) + offset_y
        sz = np.dot(rel, forward)
        projected.append((sx, sy, sz))
        if len(projected) < 5:
            log(f"[POINT] sx={sx}, sy={sy}, sz={sz:.2f}")


    log(f"[INFO] Projected {len(projected)} front-facing points")
    return projected
