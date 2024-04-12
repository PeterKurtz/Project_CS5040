"""Some utilities to help us with the data visualization."""

from collections import OrderedDict
from netCDF4 import Dataset
from dataclasses import dataclass
from datetime import datetime, date, timedelta
import zipfile
from zipfile import ZipFile

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

class WindData:
    @dataclass
    class WindVectors:
        u: np.ndarray
        v: np.ndarray

    VECTOR_CACHE_SIZE_LIMIT = 3

    zf: ZipFile
    vector_cache: OrderedDict[date, WindVectors]

    def __init__(self, filename: str):
        self.zf = ZipFile(filename)
        self.vector_cache = OrderedDict()

    def wind_vectors_by_date(self, dt: date) -> WindVectors:
        try:
            return self.vector_cache[dt]
        except KeyError:
            pass

        if len(self.vector_cache) >= WindData.VECTOR_CACHE_SIZE_LIMIT:
            self.vector_cache.popitem(last=True)

        internal_name = dt.strftime("CCMP_Wind_Analysis_%Y%m%d_V03.1_L4.nc")
        with self.zf.open(internal_name) as f:
            nc = f.read()

        ds = Dataset("dummy", memory=nc)

        uwnd = ds.variables["uwnd"]
        vwnd = ds.variables["vwnd"]

        wv = WindData.WindVectors(uwnd, vwnd)

        self.vector_cache[dt] = wv

        return wv

    def get_adjoining_slices(self, dt: datetime) -> WindVectors:
        date1 = dt.date()
        date2 = (dt + timedelta(hours=6)).date()
        point1 = dt.hour // 6
        point2 = (point1 + 1) % 4

        wv1 = self.wind_vectors_by_date(date1)
        if date1 == date2:
            return WindData.WindVectors(wv1.u[point1:point2+1], wv1.v[point1:point2+1])

        wv2 = self.wind_vectors_by_date(date2)

        unew = np.asarray([wv1.u[point1], wv2.u[point2]])
        vnew = np.asarray([wv1.v[point1], wv2.v[point2]])

        return WindData.WindVectors(unew, vnew)

    def get_wind_vector(self, dt: datetime, lat: float, lon: float):
        nclat, nclon = deg2nc((lat, lon))

        time_of_day = dt.time()

        # total seconds since last snapshot
        total_seconds = (
            time_of_day.second +
            time_of_day.minute * 60 +
            (time_of_day.hour % 6) * 60 * 60
        )

        # fraction of the time between snapshots that it has been
        time_fraction = total_seconds / (6 * 60 * 60)

        wv = self.get_adjoining_slices(dt)

        return (
            trilinear_interpolation(time_fraction, nclat, nclon, wv.u),
            trilinear_interpolation(time_fraction, nclat, nclon, wv.v),
        )
