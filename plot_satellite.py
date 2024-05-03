#! /usr/bin/env python3
"""Plot satellite data."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from plots import Map
from readers import Satellite, get_mesonh

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

cmap = LinearSegmentedColormap.from_list(
    "",
    [
        (0.0, "purple"),
        (0.1, "blue"),
        (0.2, "cyan"),
        (0.3, "lime"),
        (0.4, "green"),
        (0.5, "white"),
        (1.0, "black"),
    ],
)


def plot_satellite(satellite: Satellite, sat_map: Map, *, zoom: str = "corsica"):
    """
    Plot brightness temperature from satellite data.

    Parameters
    ----------
    satellite : Satellite
        A Satellite reader instance.
    sat_map : Map
        The Map instance to draw on.
    zoom : str, keyword-only, optionnal
        Be default it's set on ``corsica``. Accepted values are:

        * ``corsica`` : plots a domain centered on Corsica;

        * ``mesonh`` : plots the same domain as Meso-NH simulation.

        If the given value doesn't match, it plots on Corsica.
    """
    plt.close("all")
    brightness_temp = satellite.get_var("Tb")

    date = (
        datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        + timedelta(days=float(satellite.get_var("time")))
    ).strftime("%Y-%m-%d %H:%M")

    axes = sat_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"}, feature_kw={"color": "black"}
    )[1]
    if zoom == "mesonh":
        mesonh = get_mesonh(250)
        axes.set_extent((
            mesonh.longitude[0, 0],
            mesonh.longitude[-1, -1],
            mesonh.latitude[0, 0],
            mesonh.latitude[-1, -1]
        ))
    else:
        axes.set_extent((2.5, 10.5, 40, 45))

    axes.set_title(f"Mesure de température de brillance (satellite)\n{date} TU")

    contourf = sat_map.plot_contourf(
        brightness_temp, cmap=cmap, extend="min", norm=TwoSlopeNorm(235), levels=levels
    )
    plt.colorbar(contourf, label="Température de brillance (K)")

    plt.savefig(f"satellite_{date}.png")


if __name__ == "__main__":
    reader = Satellite(
        [
            f"../Donnees/satellite/data_zoom/merg_20220818{str(time_index).zfill(2)}_4km-pixel.nc4"
            for time_index in range(13)
        ],
        0,
    )
    mymap = Map(reader.longitude, reader.latitude)

    var_min, var_max = reader.get_limits("Tb")
    levels = np.linspace(210, var_max, 100)

    for reader.time_step in range(2):
        for i in range(13):
            reader.get_data(i)
            plot_satellite(reader, mymap, zoom="mesonh")
