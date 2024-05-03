#! /usr/bin/env python3
"""Plots temporal profile from stations and Meso-NH simulation."""

import json

import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

from readers import MesoNH, get_mesonh, lonlat_to_index


plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

def show_stations(mesonh_avg: bool = False):
    """
    Show the given name on a map on the given coordinates.

    Parameters
    ----------
    mesonh : MesoNH
        A MesoNH reader instance
    lon : float
        The targeted longitude.
    lat : float
        The targeted latitude.
    name : str
        The text to display at the given coordinates.
    size : int, optionnal
        The size of the spatial average.
    """
    plt.figure()
    axes = plt.axes(projection=ccrs.PlateCarree())
    axes.add_feature(cfeature.COASTLINE, linewidth=1, alpha=1)
    axes.add_feature(cfeature.BORDERS, linewidth=1, alpha=1)
    axes.add_feature(cfeature.OCEAN)
    glines = axes.gridlines(draw_labels=True, color="black", linestyle="dashed", alpha=0.5)
    glines.top_labels = glines.right_labels = False

    mesonh = get_mesonh(250)
    axes.set_extent((8.189, 10.13, 41.21, 43.45))

    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())

    for name in pos_stations:
        lat, lon = pos_stations[name]
        axes.plot(lon, lat, "o", color="red", transform=ccrs.PlateCarree())
        axes.text(lon, lat, f"\\textbf{{{name.title()}}}", color="black")

        if mesonh_avg:
            i, j = lonlat_to_index(mesonh, lon, lat)
            size = 1
            lons = mesonh.longitude[j - size, i - size], mesonh.longitude[j + size, i + size]
            lats = mesonh.latitude[j - size, i - size], mesonh.latitude[j + size, i + size]
            axes.add_patch(mpatches.Rectangle(
                xy = [lons[0], lats[0]],
                width=lons[1] - lons[0],
                height=lats[1] - lats[0],
                edgecolor="black",
                facecolor="black",
                alpha=0.5,
                transform=ccrs.PlateCarree()
            ))
    
    plt.show()


def show_station(name: str):
    plt.figure()
    axes = plt.axes(projection=ccrs.PlateCarree())
    axes.add_feature(cfeature.COASTLINE, linewidth=1, alpha=1)
    axes.add_feature(cfeature.BORDERS, linewidth=1, alpha=1)
    axes.add_feature(cfeature.OCEAN)
    glines = axes.gridlines(draw_labels=True, color="black", linestyle="dashed", alpha=0.5)
    glines.top_labels = glines.right_labels = False

    mesonh = get_mesonh(1000)
    axes.set_extent((
        mesonh.longitude[0, 0],
        mesonh.longitude[-1, -1],
        mesonh.latitude[0, 0],
        mesonh.latitude[-1, -1],
    ))

    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())

    lat, lon = pos_stations[name]
    axes.plot(lon, lat, "o", color="red", transform=ccrs.PlateCarree())
    axes.text(lon, lat, f"\\textbf{{{name.title()}}}", color="black")

    for resol_dx, size, color in ((250, 4, "C0"), (500, 2, "C1"), (1000, 1, "C2")):
        mesonh = get_mesonh(resol_dx)
        i, j = lonlat_to_index(mesonh, lon, lat)
        lons = mesonh.longitude[j - size, i - size], mesonh.longitude[j + size, i + size]
        lats = mesonh.latitude[j - size, i - size], mesonh.latitude[j + size, i + size]
        axes.add_patch(mpatches.Rectangle(
            xy = [lons[0], lats[0]],
            width=lons[1] - lons[0],
            height=lats[1] - lats[0],
            edgecolor=color,
            linewidth=2,
            facecolor="none",
            transform=ccrs.PlateCarree(),
            label=f"DX = {resol_dx}m"
        ))

    plt.legend()
    plt.show()


def get_wind10(lon: float, lat: float, resol_dx: int):
    """
    Calculate the average wind at 10 m over the last ten minutes and over an surface that depends on
    the given resolution for each hour of simulation.

        ┌───────┬────────┬─────────┐
        │  DX   │ LENGTH │ SURFACE │
        ├───────┼────────┼─────────┤
        │ 250m  │ 0.750m │ 0.56km² │
        │ 500m  │ 1.5km  │ 1.5km²  │
        │ 1000m │ 3km    │ 9km²    │
        └───────┴────────┴─────────┘

    Parameters
    ----------
    lon : float
        The longitude of the center of the surface to be averaged.
    lat : float
        The latitude of the center of the surface to be averaged.
    resol_dx : int
        The resolution of the simulation.

    Returns
    -------
    wind10 : list
        A list that contains one average value for each hour.
    """
    mesonh = get_mesonh(resol_dx)
    size = 1000 // resol_dx
    i, j = lonlat_to_index(mesonh, lon, lat)

    wind10 = []
    for time in range(61, len(mesonh.files) + 1, 60):
        wind10.append(
            3.6 * mesonh.get_mean(i, j, "WIND10", t_range=range(time - 10, time + 1), size=size)
        )
    return wind10


def get_pressure(lon: float, lat: float, resol_dx: int):
    """
    Calculate the average pressure at sea level over an surface that depends on the given resolution
    for each hour of simulation. The surfaces are the same as for ``get_wind10``.

    Parameters
    ----------
    lon : float
        The longitude of the center of the surface to be averaged.
    lat : float
        The latitude of the center of the surface to be averaged.
    resol_dx : int
        The resolution of the simulation.

    Returns
    -------
    pressure : list
        A list that contains one average value for each hour.
    """
    mesonh = get_mesonh(resol_dx)
    size = 1000 // resol_dx
    i, j = lonlat_to_index(mesonh, lon, lat)

    pressure = []
    for time in range(1, 361, 60):
        pressure.append(mesonh.get_mean(i, j, "MSLP", t_range=(time,), size=size))
    return pressure


def plot_wind(name: str):
    """
    Plot on a axe the wind at 10 meters, averaged over the ten last minutes for the three
    resolutions and from observations.

    You should have at least two files:

    * a file ``stations.json`` that contains the coordinates of each station in decimal degrees;

    * a CSV file per station.

    .. note::
        Please note that the key in the JSON file should be also the name of the CSV file.

    Parameters
    ----------
    name : str
        The name of the file that contains the informations from the station.
    """
    plt.close("all")

    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())
    lat, lon = pos_stations[name]

    axes = plt.subplots(figsize=(8, 5), layout="compressed")[1]

    for resol_dx in (250, 500, 1000):
        axes.plot(
            range(5, 10), get_wind10(lon, lat, resol_dx), label=f"Simulation\nDX = {resol_dx} m"
        )

    data = pd.read_csv(f"../Donnees/stations/{name}.csv", delimiter=";")
    axes.plot((data["heure"] - 2)[2: ], data["vent"][2: ], label=f"{name.title()}")
    axes.grid("on")

    axes.set_xlabel("Heure (TU)")
    axes.set_ylabel("Vitesse du vent (km/h)")
    axes.grid("on")

    plt.legend()
    plt.savefig(f"{name}_wind.png")


def plot_pressure(name: str):
    """
    Plot on a axe the pressure at sea level for the three resolutions and from observations.

    You should have at least two files:

    * a file ``stations.json`` that contains the coordinates of each station in decimal degrees;

    * a CSV file per station.

    .. note::
        Please note that the key in the JSON file should be also the name of the CSV file.

    Parameters
    ----------
    name : str
        The name of the file that contains the informations from the station.
    """
    plt.close("all")

    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())
    lat, lon = pos_stations[name]

    axes = plt.subplots(figsize=(8, 5), layout="compressed")[1]

    for resol_dx in (250, 500, 1000):
        axes.plot(
            range(4, 10), get_pressure(lon, lat, resol_dx), label=f"Simulation\nDX = {resol_dx} m"
        )

    data = pd.read_csv(f"../Donnees/stations/{name}.csv", delimiter=";")
    axes.plot((data["heure"] - 2)[2: ], data["pression"][2: ], label=f"{name.title()}")
    axes.grid("on")

    axes.set_xlabel("Heure (TU)")
    axes.set_ylabel("Pression (hPa)")
    axes.grid("on")

    plt.legend()
    plt.savefig(f"{name}_pressure.png")


def get_all_stations():
    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())
    return list(pos_stations.keys())


if __name__ == "__main__":
    for name in get_all_stations():
        plot_wind(name)
        plot_pressure(name)
