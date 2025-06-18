"""Basic isometric projection with Y-axis rotation."""
import math


def rotate_y(x, y, z, angle_deg):
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (
        x * cos_a + z * sin_a,
        y,
        -x * sin_a + z * cos_a
    )


def rotate_z(x, y, z, angle_deg):
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (
        x * cos_a - y * sin_a,
        x * sin_a + y * cos_a,
        z
    )


def rotate_xyz(x, y, z, angle_x, angle_y, angle_z):
    """Apply 3D rotation around X, Y, then Z."""
    # Convert to radians
    ax = math.radians(angle_x)
    ay = math.radians(angle_y)
    az = math.radians(angle_z)

    # Rotate around X
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + \
        z * math.cos(ax)

    # Rotate around Y
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + \
        z * math.cos(ay)

    # Rotate around Z
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + \
        y * math.cos(az)

    return x, y, z


def project_map(map_data, angle_x=0, angle_y=0, angle_z=0, zoom=1.0,
                offset_x=0, offset_y=0):

    """Apply Y-axis rotation and flatten to 2D coords around map center."""
    projected = []

    # Compute 3D centroid of the map
    all_points = [p for row in map_data for p in row]
    cx = sum(p[0] for p in all_points) / len(all_points)
    cy = sum(p[1] for p in all_points) / len(all_points)
    cz = sum(p[2] for p in all_points) / len(all_points)

    for row in map_data:
        for x, y, z in row:
            # Center each point around the 3D centroid
            x -= cx
            y -= cy
            z -= cz

            x, y, z = rotate_xyz(x, y, z, angle_x, angle_y, angle_z)

            # Isometric projection
            screen_x = int(x * zoom) + offset_x
            screen_y = int(y * zoom - z) + offset_y

            projected.append((screen_x, screen_y, z))

    return projected
