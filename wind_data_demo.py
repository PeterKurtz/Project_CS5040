#!/usr/bin/env python3

from datetime import datetime
from utils import WindData

wd = WindData('weather.zip')

slices = wd.get_wind_vector(datetime(2013, 11, 21, 23, 45, 55), 50, 7)

print(slices)
