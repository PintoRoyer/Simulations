#!/usr/bin/env python3
"""Some tests."""

from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import MesoNH, Antilope


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 15
})

antilope_files = [
    f"../Donnees/RADAR/PRECIP_SOL_0_2208XX{str(time_index).zfill(2)}.nc"
    for time_index in range(24)
]
cmap = LinearSegmentedColormap.from_list(
    "cmap", 
    [
        "white",
        "blue",
        "cyan",
        "green", 
        "yellow",
        "orange", 
        "red",
        "purple",
        "black"
    ]
)


def plot_antilope(radar_map, antilope, zoom: bool = True):
    for i in range(23):
        plt.close("all")
        antilope.get_data(i)
        date = datetime.strptime(f"2022-08-01 {str(i).zfill(2)}:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(hours=int(antilope.data["time"][17]))

        axes = radar_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]
        if zoom:
            axes.set_extent((
                2.5,
                antilope.longitude[-1],
                antilope.latitude[-1],
                45
            ))
        
        axes.set_title(f"Précipitations mesurées par le réseau ANTILOPE\n{date} TU")
        cf = radar_map.plot_contourf(antilope.get_var("prec"), cmap=cmap, levels=np.linspace(0, 160, 100))
        cb = plt.colorbar(cf, label="Précipitation (mm)")
        cb.set_ticks(np.linspace(0, 160, 8))
        
        if zoom:
            plt.savefig(f"antilope_zoom_{date}.png")
        else:
            plt.savefig(f"antilope_{date}.png")


antilope = Antilope(antilope_files, 17)
radar_map = Map(antilope.longitude, antilope.latitude)

plot_antilope(radar_map, antilope)
