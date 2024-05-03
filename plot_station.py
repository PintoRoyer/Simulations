#! /usr/bin/env python3
"""Plots temporal profile from stations and Meso-NH simulation."""

import json

import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from plots import TemporalProfile
from readers import MesoNH, get_index, get_mesonh


def show_station(mesonh: MesoNH, lon: float, lat: float, name: str, lons, lats):
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
    axes.add_feature(cfeature.COASTLINE, linewidth=1, alpha=0.5)
    axes.add_feature(cfeature.BORDERS, linewidth=1, alpha=0.5)
    axes.set_extent(
        (
            mesonh.longitude.min(),
            mesonh.longitude.max(),
            mesonh.latitude.min(),
            mesonh.latitude.max(),
        )
    )
    axes.add_patch(mpatches.Rectangle(
        xy = [lons[0], lats[0]],
        width=lons[1] - lons[0],
        height=lats[1] - lats[0],
        facecolor="black",
        transform=ccrs.PlateCarree()
    ))
    # axes.add_patch(mpatches.Rectangle(
    #     xy = [9.35639, 43.00165],
    #     width=0.00610,
    #     height=0.00550,
    #     facecolor="black",
    #     alpha=0.75,
    #     transform=ccrs.PlateCarree()
    # ))

    glines = axes.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    glines.top_labels = glines.right_labels = False

    axes.plot(lon, lat, ".", color="black", transform=ccrs.PlateCarree())
    axes.text(lon, lat, name.title(), color="black")

    return axes


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
    i = get_index(mesonh.longitude, lon)[1]
    j = get_index(mesonh.latitude, lat)[0]

    wind10 = []
    for time in range(61, len(mesonh.files) + 1, 60):
        wind10.append(3.6 * mesonh.get_mean(i, j, "WIND10", t_range=range(time - 10, time + 1)))
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
    i = get_index(mesonh.longitude, lon)[1]
    j = get_index(mesonh.latitude, lat)[0]

    pressure = []
    for time in range(1, 361, 60):
        pressure.append(mesonh.get_mean(i, j, "MSLP", t_range=(time,)))
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
    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())
    lat, lon = pos_stations[name]

    show_station(get_mesonh(250), lon, lat, name)

    t_profile = TemporalProfile()

    for resol_dx in (250, 500, 1000):
        t_profile.add_profile_from_array(
            range(5, 10), get_wind10(lon, lat, resol_dx), label=f"Simulation\nDX = {resol_dx} m"
        )

    t_profile.add_profile_from_csv(
        f"../Donnees/stations/{name}.csv", "heure", "vent", label=f"{name.title()}"
    )

    t_profile.axes.set_xlabel("Heure (TU)")
    t_profile.axes.set_ylabel("Vitesse du vent (km/h)")
    t_profile.axes.grid("on")

    plt.legend()
    plt.show()


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
    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())
    lat, lon = pos_stations[name]

    show_station(get_mesonh(250), lon, lat, name)

    t_profile = TemporalProfile()

    for resol_dx in (250, 500, 1000):
        t_profile.add_profile_from_array(
            range(4, 10), get_pressure(lon, lat, resol_dx), label=f"Simulation\nDX = {resol_dx} m"
        )

    t_profile.add_profile_from_csv(
        f"../Donnees/stations/{name}.csv", "heure", "pression", label=f"{name.title()}"
    )

    t_profile.axes.set_xlabel("Heure (TU)")
    t_profile.axes.set_ylabel("Pression (hPa)")
    t_profile.axes.grid("on")

    plt.legend()
    plt.show()



def new_get_index(array, target):
    delta = np.abs(array - target)
    return np.array(np.where(delta == delta.min())).transpose()


if __name__ == "__main__":
    # plot_pressure("cap corse")

    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        pos_stations = json.loads(file.read())
    lat, lon = pos_stations["cap corse"]
    mesonh = get_mesonh(250)

    i = get_index(mesonh.longitude, lon)[1]
    j = get_index(mesonh.latitude, lat)[0]

    size = 1
    lons = mesonh.longitude[j - size, i - size], mesonh.longitude[j + size, i + size]
    lats = mesonh.latitude[j - size, i - size], mesonh.latitude[j + size, i + size]



    show_station(mesonh, lon, lat, "cap corse", lons, lats)
    plt.show()
