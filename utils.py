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
