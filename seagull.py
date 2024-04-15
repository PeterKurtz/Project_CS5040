import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import contextily as ctx

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

fig, ax = plt.subplots()
ax.set_aspect('equal')

ax.set_xlim(-20, 10)
ax.set_ylim(8, 55)

ctx.add_basemap(ax, crs=gdfs[list(gdfs.keys())[0]].crs.to_string())

scatter_plots = {}
for category, gdf in gdfs.items():
    scatter_plots[category] = ax.scatter([], [], marker='o', label=category)

def update(frame):
    for category, gdf in gdfs.items():

        #print(frame)

        points = gdf[gdf['date_time'] <= frame].geometry.values

        if len(points) > 0:

            last_point = points[-1]

            scatter_plots[category].set_offsets([(last_point.x, last_point.y)])


    return list(scatter_plots.values())

ani = FuncAnimation(fig, update, frames=df['date_time'], blit=True)

ax.legend()

plt.show()

