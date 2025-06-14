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


def project_map(map_data, angle=0, zoom=1.0, offset_x=0, offset_y=0):
    """Apply Y-axis rotation and flatten to 2D screen coords around map center"""
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

            rx, ry, rz = rotate_y(x, y, z, angle)

            # Isometric projection
            screen_x = int((rx - ry) * zoom) + offset_x
            screen_y = int((rx + ry) / 2 * zoom - rz) + offset_y

            projected.append((screen_x, screen_y, rz))

    return projected
