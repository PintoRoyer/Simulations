#! /usr/bin/env python3
"""Plot ANTILOPE data."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import Antilope, get_mesonh

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

cmap = LinearSegmentedColormap.from_list(
    "", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"]
)


def plot_antilope(antilope: Antilope, radar_map: Map, *, zoom: str = "all"):
    """
    Plot all the RADAR data and export fig in PNG format.

    Parameters
    ---------
    antilope : Antilope
        An Antilope reader instance.
    radar_map : Map
        The Map instance to draw on.
    zoom : str, keyword-only, optionnal
        Be default it's set on ``all``. Accepted values are:

        * ``all`` : plot all the ANTILOPE domain;

        * ``corsica`` : plots a domain centered on Corsica;

        * ``mesonh`` : plots the same domain as Meso-NH simulation.

        If the given value doesn't match, it plots all the domain.
    """
    for i in range(23):
        plt.close("all")
        antilope.get_data(i)
        date = datetime.strptime(
            f"2022-08-01 {str(i).zfill(2)}:00:00", "%Y-%m-%d %H:%M:%S"
        ) + timedelta(hours=int(antilope.data["time"][17]))

        axes = radar_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]
        if zoom == "corsica":
            axes.set_extent((2.5, antilope.longitude[-1], antilope.latitude[-1], 45))
        elif zoom == "mesonh":
            mesonh = get_mesonh(250)
            axes.set_extent((
                mesonh.longitude[0, 0],
                mesonh.longitude[-1, -1],
                mesonh.latitude[0, 0],
                mesonh.latitude[-1, -1]
            ))


        axes.set_title(f"Précipitations mesurées par le réseau ANTILOPE\n{date} TU")
        contourf = radar_map.plot_contourf(
            antilope.get_var("prec"), cmap=cmap, levels=np.linspace(0, 160, 100)
        )
        cbar = plt.colorbar(contourf, label="Précipitation (mm)")
        cbar.set_ticks(np.linspace(0, 160, 8))

        if zoom:
            plt.savefig(f"antilope_zoom_{date}.png")
        else:
            plt.savefig(f"antilope_{date}.png")


if __name__ == "__main__":
    reader = Antilope(
        [
            f"../Donnees/RADAR/PRECIP_SOL_0_2208XX{str(time_index).zfill(2)}.nc"
            for time_index in range(24)
        ],
        17,
    )
    my_map = Map(reader.longitude, reader.latitude)

    plot_antilope(reader, my_map, zoom="mesonh")
