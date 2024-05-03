#! /usr/bin/env python3
"""Plot accumulated precipitations over an hour from Meso-NH simulation."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import json

from plots import Map
from readers import MesoNH, get_mesonh

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

cmap = LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"])


def sum_clouds(thcw, thrw, thic, thsn, thgr):
    """Add up different thickness of the condensed states of water."""
    return thcw + thrw + thic + thsn + thgr


def plot_clouds(mesonh: MesoNH, clouds_map: Map, *, resol_dx: int):
    """
    Plot the clouds hour by hour from Meso-NH silulation data and export figs in PNG format.

    Parameters
    ---------
    mesonh : MesoNH
        A MesoNH reader instance.
    clouds_map : Map
        The Map instance to draw on.
    resol_dx : int, keyword-only
        The spatial resolution of the given simulation.
    """
    # Limits for colorbars
    with open("limits/lim_250m.json", "r", encoding="utf-8") as file:
        lim = json.loads(file.read())
    levels = np.linspace(lim["clouds"][0], lim["clouds"][1], 100)

    for hour in range(59, 361, 15):
        plt.close("all")
        mesonh.get_data(hour)
        clouds = mesonh.get_var("THCW", "THRW", "THIC", "THSN", "THGR", func=sum_clouds)

        date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(
            seconds=float(mesonh.data.variables["time"][0])
        )

        axes = clouds_map.init_axes(
            fig_kw={"figsize": (8, 5), "layout": "compressed"},
            feature_kw={"linewidth": 1, "color": "white", "alpha": 0.5})[1]
        contourf = clouds_map.plot_contourf(
            clouds, cmap=cmap, levels=levels
        )
        cbar = plt.colorbar(contourf, label="Épaisseur nuageuse (mm)")
        cbar.set_ticks(np.linspace(lim["clouds"][0], lim["clouds"][1], 8))
        axes.set_title(
            f"Simulation Méso-NH du {date} TU (DX = {resol_dx} m)\n"
            "Couverture nuageuse"
        )

        plt.savefig(f"clouds_{date}_{resol_dx}m.png")


if __name__ == "__main__":
    reader = get_mesonh(250)
    my_map = Map(reader.longitude, reader.latitude)
    plot_clouds(reader, my_map, resol_dx=250)

    reader = get_mesonh(500)
    my_map = Map(reader.longitude, reader.latitude)
    plot_clouds(reader, my_map, resol_dx=500)

    reader = get_mesonh(1000)
    my_map = Map(reader.longitude, reader.latitude)
    plot_clouds(reader, my_map, resol_dx=1000)
