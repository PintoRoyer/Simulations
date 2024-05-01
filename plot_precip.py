#! /usr/bin/env python3
"""Plot accumulated precipitations over an hour from Meso-NH simulation."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import MesoNH, get_mesonh

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

cmap = LinearSegmentedColormap.from_list(
    "cmap1", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"]
)


def plot_precip(mesonh: MesoNH, precip_map: Map):
    """
    Plot the accumulated precipitations hour by hour from Meso-NH silulation data and export figs
    in PNG format.

    Parameters
    ---------
    mesonh : MesoNH
        A MesoNH reader instance.
    precip_map : Map
        The Map instance to draw on.
    """
    for hour in range(1, 361, 60):
        inprr = np.zeros(mesonh.longitude.shape)
        for time_index in range(hour, hour + 59):
            mesonh.get_data(time_index)
            # x * 60 : from minutes to hour
            inprr += mesonh.get_var("INPRR", func=lambda x: x * 60)

        date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(
            seconds=float(mesonh.data.variables["time"][0])
        )

        axes = precip_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]
        # inprr * 1000 : from m to mm
        contourf = precip_map.plot_contourf(
            inprr * 1000, cmap=cmap, levels=np.linspace(0, 160, 100)
        )
        cbar = plt.colorbar(contourf, label="Précipitations accumulées (mm)")
        cbar.set_ticks(np.linspace(0, 160, 8))
        axes.set_title(
            f"Simulation Méso-NH du {date} TU (DX = 250 m)\nPrécipitation accumulées sur l'heure"
        )

        plt.savefig(f"inprr_{date}.png")


if __name__ == "__main__":
    reader = get_mesonh(250)
    my_map = Map(reader.longitude, reader.latitude)
    plot_precip(reader, my_map)
