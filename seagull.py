import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

df = pd.read_csv('bird_tracking.csv')

df['date_time'] = pd.to_datetime(df['date_time'])

gdfs = {}

for category, group in df.groupby('bird_name'):
    geometry = [Point(xy) for xy in zip(group['longitude'], group['latitude'])]
    gdfs[category] = gpd.GeoDataFrame(group, geometry=geometry, crs="EPSG:4326")

fig, ax = plt.subplots()
ax.set_aspect('equal')

ax.set_xlim(-10, 10)
ax.set_ylim(40, 60)

scatter_plots = {}
for category, gdf in gdfs.items():
    scatter_plots[category] = ax.scatter([], [], marker='o', label=category)

def update(frame):
    for category, gdf in gdfs.items():

        points = gdf[gdf['date_time'] <= frame].geometry.values

        if len(points) > 0:

            last_point = points[-1]

            scatter_plots[category].set_offsets([(last_point.x, last_point.y)])
    return list(scatter_plots.values())

ani = FuncAnimation(fig, update, frames=df['date_time'], blit=True)

ax.legend()

plt.show()

