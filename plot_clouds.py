#! /usr/bin/env python3
"""Plot accumulated precipitations over an hour from Meso-NH simulation."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import json
import cartopy.feature as cfeature

from plots import Map
from readers import MesoNH, get_mesonh, get_time_index

plt.rcParams.update({"text.usetex": False, "font.family": "serif", "font.size": 15})

# cmap = LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"])

cmap = LinearSegmentedColormap.from_list("cmap2", [
    (0, (1, 1, 1, 0)),
    (0.2, (1, 1, 1, 0.1)),
    (0.25, (1, 1, 1, 0.4)),
    (0.55, "blue"),
    (1, "red")
])


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
        
        date = str(date).replace(":", "_")
        plt.savefig(f"clouds_{date}_{resol_dx}m.png")


def plot_all_clouds(mesonh : MesoNH, clouds_map : Map, time_index, resol_dx : int):
    with open("limits/lim_250m.json", "r", encoding="utf-8") as file:
        lim = json.loads(file.read())
    levels = np.linspace(lim["clouds"][0], lim["clouds"][1], 100)
    plt.close("all")
    
    axes = clouds_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"},
        feature_kw={"linewidth": 1, "color": "white", "alpha": 0.5})[1]
    axes.add_feature(cfeature.OCEAN, color="black")
    axes.add_feature(cfeature.LAND, color="black")
    
    for time in time_index :
        mesonh.get_data(time)
        clouds = mesonh.get_var("THCW", "THRW", "THIC", "THSN", "THGR", func=sum_clouds)

        contourf = clouds_map.plot_contourf(
            clouds, cmap=cmap, levels=levels
        )
        
    cbar = plt.colorbar(contourf, label="Épaisseur nuageuse (mm)")
    cbar.set_ticks(np.linspace(lim["clouds"][0], lim["clouds"][1], 8))
    axes.set_title(
        f"Simulation Méso-NH - (DX = {resol_dx} m)\n"
        "Couverture nuageuse"
    )
    
    plt.savefig(f"clouds_{resol_dx}m.png")



if __name__ == "__main__":
    time_index = []
    time = ((5, 0), (6, 30), (7, 15), (8, 15), (8, 45))
    for hour, minute in time:
        time_index.append(get_time_index(hour, minute))
    
    # reader = get_mesonh(250)
    # my_map = Map(reader.longitude, reader.latitude)
    # plot_all_clouds(reader, my_map, time_index, resol_dx=250)

    # reader = get_mesonh(500)
    # my_map = Map(reader.longitude, reader.latitude)
    # plot_all_clouds(reader, my_map, time_index, resol_dx=500)

    reader = get_mesonh(1000)
    my_map = Map(reader.longitude, reader.latitude)
    plot_all_clouds(reader, my_map, time_index, resol_dx=1000)
