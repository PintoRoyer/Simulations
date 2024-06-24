"""
Re-adjusted accumulated precipitations
======================================

Description
-----------
Plot accumulated precipitations over an hour from Meso-NH simulations. This module also contains two
dict for the offset: LON_OFFSET and LAT_OFFSET. These dictionnary allows to re-adjust the
simulations to fit the observations.
"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from plot_station import all_stations_on_axes
from plots import Map
from readers import MesoNH

LON_OFFSET = {250: 1.151457, 500: 1.186018, 1000: 1.106474}
LAT_OFFSET = {250: 0.433702, 500: 0.448599, 1000: 0.31105}

# Matplotlib configuration to have LaTeX style
# plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

# Custom CMAP
CMAP = LinearSegmentedColormap.from_list(
    "", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"]
)


def plot_precip_inprr(mesonh: MesoNH, precip_map: Map, *, resol_dx: int, stations: bool = False):
    """
    Plot the accumulated precipitations hour by hour from Meso-NH silulation data and export figs
    in PNG format.

    Parameters
    ----------
    mesonh : MesoNH
        A MesoNH reader instance.
    precip_map : Map
        The Map instance to draw on.
    resol_dx : int, keyword-only
        The spatial resolution of the given simulation.
    stations : bool, keyword-only, optionnal
        By default it's set on False. If set on True, the positions of the stations will be
        display on the map.

    Exemples
    --------

        # Imports
        from plots import Map
        from readers import get_mesonh

        from plot_precip import plot_precip_inprr

        # Open Meso-NH at DX = 250m and create a new map with the offset
        reader = get_mesonh(250)
        my_map = Map(reader.longitude + LON_OFFSET[250], reader.latitude + LAT_OFFSET[250])

        plot_precip_inprr(reader, my_map, resol_dx=250)

    """
    # For each hour from the beginning to the end
    for hour in range(1, 361, 60):
        # Sum the instaneous precipitation rate to have accumulated precipitation over the past hour
        inprr = np.zeros(mesonh.longitude.shape)
        for time_index in range(hour, hour + 59):
            mesonh.get_data(time_index)
            # x * 60 : from minutes to hour
            inprr += mesonh.get_var("INPRR", func=lambda x: x * 60)

        # Compute the datetime
        date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(
            seconds=float(mesonh.data.variables["time"][0])
        )

        # Init the map
        axes = precip_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]

        # Add stations on the map
        if stations:
            all_stations_on_axes(axes)

        # Add contourf and colorbar
        contourf = precip_map.plot_contourf(
            inprr * 1000, cmap=CMAP, levels=np.linspace(0, 160, 100)
        )  # inprr * 1000 : from m to mm
        cbar = plt.colorbar(contourf, label="Précipitations accumulées (mm)")
        cbar.set_ticks(np.linspace(0, 160, 8))

        # Add the title
        axes.set_title(
            f"Simulation Méso-NH du {date} TU (DX = {resol_dx} m)\n"
            "Précipitation accumulées sur l'heure"
        )

        # Export the figure
        plt.savefig(f"inprr_{date}_{resol_dx}m.png")


def plot_precip_acprr(mesonh: MesoNH, precip_map: Map, *, resol_dx: int, stations: bool = False):
    """
    Plot the accumulated precipitations hour by hour from Meso-NH silulation data and export figs
    in PNG format.

    Parameters
    ----------
    mesonh : MesoNH
        A MesoNH reader instance.
    precip_map : Map
        The Map instance to draw on.
    resol_dx : int, keyword-only
        The spatial resolution of the given simulation.
    stations : bool, keyword-only, optionnal
        By default it's set on False. If set on True, the positions of the stations will be
        display on the map.

    Exemples
    --------

        # Imports
        from plots import Map
        from readers import get_mesonh

        from plot_precip import plot_precip_acprr

        # Open Meso-NH at DX = 250m and create a new map with the offset
        reader = get_mesonh(250)
        my_map = Map(reader.longitude + LON_OFFSET[250], reader.latitude + LAT_OFFSET[250])

        plot_precip_acprr(reader, my_map, resol_dx=250)

    """
    # For each hour
    for hour in range(60, 360, 60):
        # Compute the accumulated precipitation over the past hour
        mesonh.get_data(hour - 60)
        acprr_60 = mesonh.get_var("ACPRR")
        mesonh.get_data(hour)
        acprr_0 = mesonh.get_var("ACPRR")
        acprr_hourly = acprr_0 - acprr_60

        # Compute datetime
        date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(
            seconds=float(mesonh.data.variables["time"][0])
        )

        # Init axes
        axes = precip_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]

        # Add stations on the map
        if stations:
            all_stations_on_axes(axes)

        # Plot contourf and colorbar
        contourf = precip_map.plot_contourf(
            acprr_hourly * 1000, cmap=CMAP, levels=np.linspace(0, 160, 100)
        )
        cbar = plt.colorbar(contourf, label="Précipitations accumulées (mm/h)")
        cbar.set_ticks(np.linspace(0, 160, 8))
        axes.set_title(
            f"Simulation Méso-NH du {date} TU (DX = {resol_dx} m)\n"
            "Précipitation accumulées sur l'heure"
        )

        # Add the title
        axes.set_title(
            f"Simulation Méso-NH du {date} TU (DX = {resol_dx} m)\n"
            "Précipitation accumulées sur l'heure"
        )

        # Export figure
        plt.savefig(f"acprr_hourly_{date}_{resol_dx}m.png")
