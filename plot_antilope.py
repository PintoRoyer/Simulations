"""
Antilope
========

Description
-----------
This module plots the hourly accumulated precipitation from Antilope product.
"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from plot_station import all_stations_on_axes
from plots import Map
from readers import Antilope, get_mesonh

# Matplotlib configuration to have LaTeX style
# plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

# Custom colormap
CMAP = LinearSegmentedColormap.from_list(
    "", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"]
)


def plot_antilope(
    index: int, antilope: Antilope, radar_map: Map, *, zoom: str = "all", stations: bool = False
):
    """
    Plot the RADAR data and export figure in PNG format.

    Parameters
    ---------
    index : int
        The time index in the Antilope file to open.
    antilope : Antilope
        An Antilope reader instance.
    radar_map : Map
        The Map instance to draw on.
    zoom : str, keyword-only, optionnal
        Be default it's set on 'all'. Accepted values are:

        * 'all'     : plot all the ANTILOPE domain;

        * 'corsica' : plots a domain centered on Corsica;

        * 'mesonh'  : plots the same domain as Meso-NH simulation.

        If the given value doesn't match, it plots all the domain.
    stations : bool, keyword-only, optionnal
        By default it's set on False. If set on True, the positions of the stations will be
        display on the map.

    Raises
    ------
    ValueError
        This exception is raised if the given zoom isn't recognize.

    Exemples
    --------
    Assuming that the Antilope data are in the directory '../Donnees/Antilope/':

        # Imports
        from plots import Map
        from readers import Antilope, get_mesonh

        from plot_antilope import plot_antilope

        # Open Antilope data
        reader = Antilope(
            [
                f"../Donnees/Antilope/PRECIP_SOL_0_2208XX{str(time_index).zfill(2)}.nc"
                for time_index in range(24)
            ],
            17,  # Day index
        )

        # Create a new map and select file in Antilope data
        my_map = Map(reader.longitude, reader.latitude)
        reader.get_data(6)

        plot_antilope(6, reader, my_map, zoom="mesonh")

    """
    # Close all current figure
    plt.close("all")

    # Compute datetime
    date = datetime.strptime(
        f"2022-08-01 {str(index).zfill(2)}:00:00", "%Y-%m-%d %H:%M:%S"
    ) + timedelta(hours=int(antilope.data["time"][17]))

    # Init axes of the map
    axes = radar_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]

    # Manage map extent
    if zoom == "corsica":
        axes.set_extent((2.5, antilope.longitude[-1], antilope.latitude[-1], 45))
    elif zoom == "mesonh":
        mesonh = get_mesonh(250)
        axes.set_extent(
            (
                mesonh.longitude[0, 0],
                mesonh.longitude[-1, -1],
                mesonh.latitude[0, 0],
                mesonh.latitude[-1, -1],
            )
        )
    elif zoom != "all":
        raise ValueError(f"'{zoom}' isn't recognize as a zoom")

    # If stations should be plotted on the map
    if stations:
        all_stations_on_axes(axes)

    # Set fig title
    axes.set_title(f"Précipitations mesurées par le réseau ANTILOPE\n{date} TU")

    # Add contourf and a colorbar
    contourf = radar_map.plot_contourf(
        antilope.get_var("prec"), cmap=CMAP, levels=np.linspace(0, 160, 100)
    )
    cbar = plt.colorbar(contourf, label="Précipitation (mm)")
    cbar.set_ticks(np.linspace(0, 160, 8))

    # Save the fig
    if zoom:
        plt.savefig(f"antilope_zoom_{date}.png")
    else:
        plt.savefig(f"antilope_{date}.png")
