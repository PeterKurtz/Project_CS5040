import sys
from functools import cache
import pandas as pd
import geopandas as gpd
from pandas.core.arrays.datetimes import datetime
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import contextily as ctx
from utils import WindData

COLORS = {
    "Eric": "tab:orange",
    "Nico": "tab:blue",
    "Sanne": "tab:green",
}

action = 'draw'

if len(sys.argv) >= 2:
    action = sys.argv[1]

ARROW_SCALE_FACTOR = 0.3

df = pd.read_csv('bird_tracking.csv')

#Test 2013-11-01, 2013-11-17

print("Choose a date to start between 2013-08-15 and 2014-04-30 of format yyyy-mm-dd")
dateStart = input()
dateStart +=  ' 00:00:00+00'
dateStart = pd.to_datetime(dateStart)

df['date_time'] = pd.to_datetime(df['date_time'])

df = df[df['date_time'] >= dateStart]

gdfs = {}

for category, group in df.groupby('bird_name'):
    geometry = [Point(xy) for xy in zip(group['longitude'], group['latitude'])]
    gdfs[category] = gpd.GeoDataFrame(group, geometry=geometry, crs="EPSG:4326")

fig, ax = plt.subplots(figsize=(9, 15), dpi=120)
ax.set_aspect('equal')

ax.set_xlim(-20, 10)
ax.set_ylim(0, 55)

ctx.add_basemap(ax, crs=gdfs[list(gdfs.keys())[0]].crs.to_string())

artists = {}
for category, gdf in gdfs.items():
    artists[category] = ax.scatter([], [], marker='o', label=category, color=COLORS[category])
    artists[f"arrow_{category}"] = ax.arrow(0, 0, 0, 0, color=COLORS[category], width=0.04, head_width=0.2)

artists["text"] = ax.text(-19, 54, "", fontfamily="monospace")

wind_data = WindData("weather.zip")

last_time = dateStart

def update(frame):
    global last_time

    if frame < last_time:
        ani.event_source.stop()
        plt.close(fig)
        sys.exit(0) # I had to make it exit uncleanly because render wouldn't work with just the other code

    last_time = frame

    artists["text"].set_text(frame.strftime("%Y-%m-%d %H:%M:%S"))

    for category, gdf in gdfs.items():
        print(frame)

        points = gdf[gdf['date_time'] <= frame].geometry.values
        if len(points) > 0:
            last_point = points[-1]
            dx, dy = wind_data.get_wind_vector(frame, last_point.x, last_point.y)

            artists[category].set_offsets([(last_point.x, last_point.y)])
            artists[f"arrow_{category}"].set_data(x=last_point.x, y=last_point.y, dx=dx * ARROW_SCALE_FACTOR, dy=dy * ARROW_SCALE_FACTOR)

    return list(artists.values())

ani = FuncAnimation(fig, update, frames=df['date_time'], blit=True, repeat=False)

ax.legend()

if action == 'render':
    ani.save(filename='./ffmpeg-test.mkv', writer='ffmpeg')
else:
    plt.show()
