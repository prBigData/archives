import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import json


def show_vessels(d):
    """vessels shower"""
    fig = plt.figure()
    themap = Basemap(
        projection='gall',
        llcrnrlon=-4,              # lower-left corner longitude
        llcrnrlat=26,               # lower-left corner latitude
        urcrnrlon=37,               # upper-right corner longitude
        urcrnrlat=48,               # upper-right corner latitude
        resolution='l',
        area_thresh=100000.0,
    )

    themap.drawcoastlines()
    themap.drawcountries()
    themap.fillcontinents(color='gainsboro')
    themap.drawmapboundary(fill_color='steelblue')

    # d is a list of vessel dicts
    for v in d:
        lon = float(v['LONG'])
        lat = float(v['LAT'])
        x, y = themap(lon, lat)
        themap.plot(x, y, 'bo', markersize=4)

    plt.show()
