"""
Clouds concatenation
====================

Description
-----------
This module allow to plot a time concatenation of clouds from the Meso-NH simulations.
"""

import json

import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import MesoNH

# Matplotlib configuration to have LaTeX style
# plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

# Custom colormap
CMAP = LinearSegmentedColormap.from_list(
    "",
    [(0, (1, 1, 1, 0)), (0.2, (1, 1, 1, 0.1)), (0.25, (1, 1, 1, 0.4)), (0.55, "blue"), (1, "red")],
)


def sum_clouds(thcw, thrw, thic, thsn, thgr):
    """Add up different thickness of the condensed states of water."""
    return thcw + thrw + thic + thsn + thgr


def plot_concat_clouds(mesonh: MesoNH, clouds_map: Map, *, time_index: list, resol_dx: int):
    """
    Plot the clouds at different time indices on a unique figure and export it in PNG format.

    Parameters
    ----------
    mesonh : MesoNH
        A MesoNH reader instance.
    clouds_map : Map
        The Map instance to draw on.
    time_index : list, keyword-only
        The indices to plot on the map.
    resol_dx : int, keyword-only
        The spatial resolution of the given simulation.

    Exemples
    --------

        # Imports
        from plots import Map
        from readers import get_mesonh, get_time_index

        from plot_clouds import plot_concat_clouds

        # Calculate time index from (hour, minutes)
        time_index = [
            get_time_index(hour, minute)
            for hour, minute in ((5, 0), (6, 30), (7, 15), (8, 15), (8, 45))
        ]

        # Open Meso-NH at DX = 250m and create a map
        reader = get_mesonh(250)
        my_map = Map(reader.longitude, reader.latitude)

        plot_concat_clouds(reader, my_map, time_index=time_index, resol_dx=250)

    """
    # Close all the current figures
    plt.close("all")

    # Fit the limits for the levels of contourf
    with open("limits/lim_250m.json", "r", encoding="utf-8") as file:
        lim = json.loads(file.read())
    levels = np.linspace(lim["clouds"][0], lim["clouds"][1], 100)

    # Init the map axes
    axes = clouds_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"},
        feature_kw={"linewidth": 1, "color": "white", "alpha": 0.5},
    )[1]
    axes.add_feature(cfeature.OCEAN, color="black")
    axes.add_feature(cfeature.LAND, color="black")

    # Add contourf for each time index
    for time in time_index:
        mesonh.get_data(time)
        clouds = mesonh.get_var("THCW", "THRW", "THIC", "THSN", "THGR", func=sum_clouds)

        contourf = clouds_map.plot_contourf(clouds, cmap=CMAP, levels=levels)

    # Configure the colorbar
    cbar = plt.colorbar(contourf, label="Épaisseur nuageuse (mm)")
    cbar.set_ticks(np.linspace(lim["clouds"][0], lim["clouds"][1], 8))
    axes.set_title(f"Simulation Méso-NH - (DX = {resol_dx} m)\n" "Couverture nuageuse")

    # Export the figure
    plt.savefig(f"clouds_{resol_dx}m_5.png")
