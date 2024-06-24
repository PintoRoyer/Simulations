"""
Stations
========

Description
-----------
Plots temporal profile from stations and Meso-NH simulation.
"""

import json

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from readers import get_mesonh, lonlat_to_index

LON_OFFSET = {250: 1.151457, 500: 1.186018, 1000: 1.106474}
LAT_OFFSET = {250: 0.433702, 500: 0.448599, 1000: 0.31105}

# Matplotlib configuration to have LaTeX style
# plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})


def get_all_stations():
    """Returns all the stations in the json file."""
    with open("../Donnees/stations/stations.json", "r", encoding="utf-8") as file:
        stations = json.loads(file.read())
    return stations


def all_stations_on_axes(axes: plt.Axes, dlon: float = 0, dlat: float = 0):
    """
    Plot all the known stations on a given axes.

    Parameters
    ----------
    axes : plt.Axes
        The axes to show the stations on.
    dlon : float, optionnal
        By default: 0. The offset on longitude.
    dlat : float, optionnal
        By default: 0. The offset on latitude.
    """
    stations = get_all_stations()

    for name in stations:
        lat, lon = stations[name]
        station_on_axes(axes, lon + dlon, lat + dlat, name)


def station_on_axes(axes: plt.Axes, lon: float, lat: float, name: str):
    """
    Plot the given stations on an axes.

    Parameters
    ----------
    axes : plt.Axes
        The axes to show the stations on.
    lon : float
        Station longitude.
    lat : float
        Station latitude.
    name : str
        The name of the station.
    """
    axes.plot(lon, lat, "o", color="red", transform=ccrs.PlateCarree())
    axes.text(lon, lat, f"\\textbf{{{name.title()}}}", color="black")


def show_stations(mesonh_avg: bool = False):
    """
    Show all stations on a map.

    Parameters
    ----------
    mesonh_avg : bool, optionnal
        By default it's set on False. If set on True, the area over which the average for virtual
        stations are computed will be displayed.
    """
    # Create a new figure and a new axe
    plt.figure()
    axes = plt.axes(projection=ccrs.PlateCarree())
    axes.add_feature(cfeature.COASTLINE, linewidth=1, alpha=1)
    axes.add_feature(cfeature.BORDERS, linewidth=1, alpha=1)
    axes.add_feature(cfeature.OCEAN)
    glines = axes.gridlines(draw_labels=True, color="black", linestyle="dashed", alpha=0.5)
    glines.top_labels = glines.right_labels = False

    # Open Meso-NH simulation and set extent
    mesonh = get_mesonh(250)
    axes.set_extent((8.189, 10.13, 41.21, 43.45))

    # Get all the known stations
    stations = get_all_stations()

    for name in stations:
        # Plot the station on axes
        lat, lon = stations[name]
        station_on_axes(axes, lon, lat, name)

        # Display the area over which the average is computed
        if mesonh_avg:
            i, j = lonlat_to_index(mesonh, lon, lat)
            size = 1
            lons = mesonh.longitude[j - size, i - size], mesonh.longitude[j + size, i + size]
            lats = mesonh.latitude[j - size, i - size], mesonh.latitude[j + size, i + size]
            axes.add_patch(
                mpatches.Rectangle(
                    xy=[lons[0], lats[0]],
                    width=lons[1] - lons[0],
                    height=lats[1] - lats[0],
                    edgecolor="black",
                    facecolor="black",
                    alpha=0.5,
                    transform=ccrs.PlateCarree(),
                )
            )

    # Show the fig
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
    wind10_std = []
    for time in range(60, len(mesonh.files) + 1, 6):
        limits, mean, std = mesonh.get_stats(
            i, j, "WIND10", func=lambda x: x * 3.6, t_range=range(time - 11, time), size=size
        )
        print(f"{str(time // 60 + 4).zfill(2)}h{str(time % 60).zfill(2)} TU")
        print(f".. limites    : {limits[0]:.2f} km/h -- {limits[1]:.2f} km/h")
        print(f".. moyenne    : {mean:.2f} km/h")
        print(f".. écart-type : {std:.2f} km/h")
        wind10.append(mean)
        wind10_std.append(std)

    print()
    return wind10, wind10_std


def get_pressure(lon: float, lat: float, resol_dx: int):
    """
    Calculate the average pressure at sea level over an surface that depends on the given resolution
    for each hour of simulation. The surfaces are the same as for get_wind10.

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
    pressure_std = []
    for time in range(1, len(mesonh.files) + 1, 6):
        limits, mean, std = mesonh.get_stats(i, j, "MSLP", t_range=(time,), size=size)

        print(f"{str(time // 60 + 4).zfill(2)}h{str(time % 60).zfill(2)} TU")
        print(f".. limites    : {limits[0]:.2f} hPa -- {limits[1]:.2f} hPa")
        print(f".. moyenne    : {mean:.2f} hpa")
        print(f".. écart-type : {std:.2f} hpa")
        pressure.append(mean)
        pressure_std.append(std)

    print()
    return pressure, pressure_std


def plot_wind(name: str):
    """
    Plot on a axe the wind at 10 meters, averaged over the ten last minutes for the three
    resolutions and from observations.

    You should have at least two files:

    * a file stations.json that contains the coordinates of each station in decimal degrees;

    * a CSV file per station.

    .. note::
        Please note that the key in the JSON file should be also the name of the CSV file.

    Parameters
    ----------
    name : str
        The name of the file that contains the informations from the station.
    """
    # Close all fig
    plt.close("all")

    # Get the coords of requested stations
    stations = get_all_stations()
    lat, lon = stations[name]

    # Init axes
    axes = plt.subplots(figsize=(8, 5), layout="compressed")[1]

    # Extract the data on virtual station
    for resol_dx in (250,):
        title = f"Vent {name.title()} DX = {resol_dx} m"
        print(f"{title}\n" + len(title) * "-")

        # Compute average over
        mean, std = get_wind10(lon, lat, resol_dx)
        axes.errorbar(range(51), mean, yerr=std, fmt="o", label=f"Simulation\nDX = {resol_dx} m")

        # Compute average on re-adjusted
        mean, std = get_wind10(lon - LON_OFFSET[resol_dx], lat - LAT_OFFSET[resol_dx], resol_dx)
        axes.errorbar(
            range(51), mean, yerr=std, fmt="o", label=f"Simulation recalée\nDX = {resol_dx} m"
        )

    # Add observation on the plot
    data = pd.read_csv(f"../Donnees/stations/{name}_station_20220818.csv", delimiter=";")
    axes.plot(range(51), data["wind_spd"][70:121], "o", label=f"{name.title()}")
    axes.grid("on")

    # Configure axes
    axes.set_xticks(range(0, 51, 5), data["time (local)"].values[50:101:5])
    axes.set_xlabel("Heure (TU)")
    axes.set_ylabel("Vitesse du vent (km/h)")
    axes.grid("on")

    # Add legend and export figure
    plt.legend()
    plt.savefig(f"{name}_wind_{resol_dx}m.png")


def plot_pressure(name: str):
    """
    Plot on a axe the pressure at sea level for the three resolutions and from observations.

    You should have at least two files:

    * a file stations.json that contains the coordinates of each station in decimal degrees;

    * a CSV file per station.

    .. note::
        Please note that the key in the JSON file should be also the name of the CSV file.

    Parameters
    ----------
    name : str
        The name of the file that contains the informations from the station.
    """
    # Close all fig
    plt.close("all")

    # Extract requested fig
    stations = get_all_stations()
    lat, lon = stations[name]

    # Init axes
    axes = plt.subplots(figsize=(8, 5), layout="compressed")[1]

    # Extract the data on virtual station
    for resol_dx in (250,):
        title = f"Pression {name.title()} DX = {resol_dx} m"
        print(f"{title}\n" + len(title) * "-")

        mean, std = get_pressure(lon, lat, resol_dx)
        axes.errorbar(
            np.arange(4, 10, 0.1), mean, yerr=std, fmt="o", label=f"Simulation\nDX = {resol_dx} m"
        )

        mean, std = get_pressure(lon - LON_OFFSET[resol_dx], lat - LAT_OFFSET[resol_dx], resol_dx)
        axes.errorbar(
            np.arange(4, 10, 0.1),
            mean,
            yerr=std,
            fmt="o",
            label=f"Simulation recalée\nDX = {resol_dx} m",
        )

    # add data from observations
    data = pd.read_csv(f"../Donnees/stations/{name}.csv", delimiter=";")
    axes.plot((data["heure"] - 2)[5:14], data["pression"][5:14], label=f"{name.title()}")
    axes.grid("on")

    # Configure axes
    axes.set_xlabel("Heure (TU)")
    axes.set_ylabel("Pression (hPa)")
    axes.grid("on")

    # Add legend and savefig
    plt.legend()
    plt.savefig(f"{name}_pressure_{resol_dx}m.png")
