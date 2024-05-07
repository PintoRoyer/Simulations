#! /usr/bin/env python3
"""Plot satellite data."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from plots import Map
from readers import Satellite, get_mesonh
from plot_station import get_all_stations, all_stations_on_axes


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


def plot_satellite(
    satellite: Satellite,
    sat_map: Map,
    *,
    levels: np.array,
    zoom: str = "corsica",
    stations: bool = False
):
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
    stations : bool, keyword-only, optionnal
        By default it's set on ``False``. If set on ``True``, the positions of the stations will be
        display on the map.
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

    if stations:
        all_stations_on_axes(axes)

    axes.set_title(f"Mesure de température de brillance (satellite)\n{date} TU")

    contourf = sat_map.plot_contourf(
        brightness_temp, cmap=cmap, extend="min", norm=TwoSlopeNorm(235), levels=levels
    )
    plt.colorbar(contourf, label="Température de brillance (K)")

    plt.show()
    # plt.savefig(f"satellite_{date}.png")


if __name__ == "__main__":
    reader = Satellite(
        [
            f"../Donnees/satellite/data_zoom/merg_20220818{str(time_index).zfill(2)}_4km-pixel.nc4"
            for time_index in range(13)
        ],
        1,
    )
    mymap = Map(reader.longitude, reader.latitude)

    var_min, var_max = reader.get_limits("Tb")
    levels = np.linspace(210, var_max, 100)

    reader.get_data(6)
    plot_satellite(reader, mymap, levels=levels, zoom="mesonh", stations=True)
