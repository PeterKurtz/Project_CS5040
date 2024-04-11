"""Some utilities to help us with the data visualization."""

def deg2nc_lat(deg: float) -> float:
    """Transform a latitude in degrees into netCDF-native coordinates."""
    return (-deg + 90) * 4

def deg2nc_lon(deg: float) -> float:
    """Transform a longitude in degrees into netCDF-native coordinates."""
    return (deg + 180) * 4

def deg2nc(deg: tuple[float, float]) -> tuple[float, float]:
    """Transform a (latitude, longitude) pair in degrees into netCDF-native coordinates."""
    return (deg2nc_lat(deg[0]), deg2nc_lon(deg[1]))

def nc2deg_lat(nc: float) -> float:
    """Transform a latitude in netCDF-native coordinates into degrees."""
    return -nc / 4 - 90

def nc2deg_lon(nc: float) -> float:
    """Transform a longitude in netCDF-native coordinates into degrees."""
    return nc / 4 - 180

def nc2deg(nc: tuple[float, float]) -> tuple[float, float]:
    """Transform a (latitude, longitude) pair in netCDF-native coordinates into degrees."""
    return (nc2deg_lat(nc[0]), nc2deg_lon(nc[1]))

import numpy as np

def trilinear_interpolation(x, y, z, data):
    # Get the dimensions of the data cube
    x_dim, y_dim, z_dim, *_more_dims = data.shape
    
    # Make sure the interpolation point is within the bounds of the data
    if (x < 0 or x >= x_dim - 1 or
        y < 0 or y >= y_dim - 1 or
        z < 0 or z >= z_dim - 1):
        raise ValueError("Interpolation point is outside the data bounds")
    
    # Compute the fractional parts of the indices
    x0, y0, z0 = int(x), int(y), int(z)
    x1, y1, z1 = x0 + 1, y0 + 1, z0 + 1
    dx, dy, dz = x - x0, y - y0, z - z0
    
    # Perform trilinear interpolation
    interpolated_value = (
        (1 - dx) * (1 - dy) * (1 - dz) * data[x0, y0, z0] +
        dx * (1 - dy) * (1 - dz) * data[x1, y0, z0] +
        (1 - dx) * dy * (1 - dz) * data[x0, y1, z0] +
        dx * dy * (1 - dz) * data[x1, y1, z0] +
        (1 - dx) * (1 - dy) * dz * data[x0, y0, z1] +
        dx * (1 - dy) * dz * data[x1, y0, z1] +
        (1 - dx) * dy * dz * data[x0, y1, z1] +
        dx * dy * dz * data[x1, y1, z1]
    )
    
    return interpolated_value
