"""
Satellite
=========

Description
-----------
Plot satellite brightness temperature
"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from plot_station import all_stations_on_axes
from plots import Map
from readers import Satellite, get_mesonh

# Matplotlib configuration to have LaTeX style
# plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

# Custom colorbar
CMAP = LinearSegmentedColormap.from_list(
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


def plot_satellite_brightness_temp(
    satellite: Satellite,
    sat_map: Map,
    *,
    levels: np.array,
    zoom: str = "corsica",
    stations: bool = False,
):
    """
    Plot brightness temperature from satellite data.

    Parameters
    ----------
    satellite : Satellite
        A Satellite reader instance.
    sat_map : Map
        The Map instance to draw on.
    levels : np.array, keyword-only
        The levels for the contourf
    zoom : str, keyword-only, optionnal
        Be default it's set on 'corsica'. Accepted values are:

        * 'corsica' : plots a domain centered on Corsica;

        * 'mesonh'  : plots the same domain as Meso-NH simulation.

        If the given value doesn't match, it plots on Corsica.
    stations : bool, keyword-only, optionnal
        By default it's set on False. If set on True, the positions of the stations will be
        display on the map.

    Raises
    ------
    ValueError
        This exception is raised if the given zoom isn't recognize.

    Exemples
    --------

        # Imports
        from plots import Map
        from reader import Satellite

        from plot_satellite import plot_satellite_brightness_temp

        # Open satellite files
        reader = Satellite(
            [
                f"../Donnees/satellite/data_zoom/merg_20220818{str(time_index).zfill(2)}_4km-pixel"
                f".nc4"
                for time_index in range(13)
            ],
            1,
        )

        # Create a new map
        mymap = Map(reader.longitude, reader.latitude)

        # Compute levels for contourf
        var_min, var_max = reader.get_limits("Tb")
        levels = np.linspace(210, var_max, 100)

        # Open sixth file and plot data
        reader.get_data(6)
        plot_satellite_brightness_temp(reader, mymap, levels=levels, zoom="mesonh", stations=True)

    """
    # Close all current fig
    plt.close("all")

    # Extract brightness temperature from satellite file
    brightness_temp = satellite.get_var("Tb")

    # Compute datetime
    date = (
        datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        + timedelta(days=float(satellite.get_var("time")))
    ).strftime("%Y-%m-%d %H:%M")

    # Init axes
    axes = sat_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"}, feature_kw={"color": "black"}
    )[1]

    # Manage map extent
    if zoom == "corsica":
        axes.set_extent((2.5, 10.5, 40, 45))
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

    # Plot stations if requested
    if stations:
        all_stations_on_axes(axes)

    # Add title
    axes.set_title(f"Mesure de température de brillance (satellite)\n{date} TU")

    # Add contourf and colorbar to the map
    contourf = sat_map.plot_contourf(
        brightness_temp, cmap=CMAP, extend="min", norm=TwoSlopeNorm(235), levels=levels
    )
    plt.colorbar(contourf, label="Température de brillance (K)")

    # Export figure
    plt.savefig(f"satellite_{date}.png")
