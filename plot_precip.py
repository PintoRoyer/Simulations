#! /usr/bin/env python3
"""Plot accumulated precipitations over an hour from Meso-NH simulation."""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import MesoNH, get_mesonh
from plot_station import all_stations_on_axes, station_on_axes


LON_OFFSET = {
    250:  1.151457,
    500:  1.186018,
    1000: 1.106474
}
LAT_OFFSET = {
    250:  0.433702,
    500:  0.448599,
    1000: 0.31105
}

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})

cmap = LinearSegmentedColormap.from_list(
    "cmap1", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"]
)


def plot_precip_inprr(mesonh: MesoNH, precip_map: Map, *, resol_dx: int, stations: bool = False):
    """
    Plot the accumulated precipitations hour by hour from Meso-NH silulation data and export figs
    in PNG format.

    Parameters
    ---------
    mesonh : MesoNH
        A MesoNH reader instance.
    precip_map : Map
        The Map instance to draw on.
    resol_dx : int, keyword-only
        The spatial resolution of the given simulation.
    stations : bool, keyword-only, optionnal
        By default it's set on ``False``. If set on ``True``, the positions of the stations will be
        display on the map.
    """
    # for hour in range(1, 361, 60):
    for hour in (121, ):
        inprr = np.zeros(mesonh.longitude.shape)
        for time_index in range(hour, hour + 59):
            mesonh.get_data(time_index)
            # x * 60 : from minutes to hour
            inprr += mesonh.get_var("INPRR", func=lambda x: x * 60)

        date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(
            seconds=float(mesonh.data.variables["time"][0])
        )

        axes = precip_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]

        if stations:
            all_stations_on_axes(axes)

        station_on_axes(axes, 8.65528, 42.18889, "Marignana")

        # inprr * 1000 : from m to mm
        contourf = precip_map.plot_contourf(
            inprr * 1000, cmap=cmap, levels=np.linspace(0, 160, 100)
        )
        cbar = plt.colorbar(contourf, label="Précipitations accumulées (mm)")
        cbar.set_ticks(np.linspace(0, 160, 8))
        axes.set_title(
            f"Simulation Méso-NH du {date} TU (DX = {resol_dx} m)\n"
            "Précipitation accumulées sur l'heure"
        )

        plt.show()
        # plt.savefig(f"inprr_{date}_{resol_dx}m.png")


def plot_precip_acprr(mesonh: MesoNH, precip_map : Map, resol_dx : int):
    for hour in range (60, 360, 60):
        mesonh.get_data(hour - 60)
        acprr_60 = mesonh.get_var("ACPRR")
        mesonh.get_data(hour)
        acprr_0 = mesonh.get_var("ACPRR")
        
        acprr_hourly = acprr_0 - acprr_60
        
        
        date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(
            seconds=float(mesonh.data.variables["time"][0])
        )
       
        axes = precip_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]
        contourf = precip_map.plot_contourf(
            acprr_hourly * 1000, cmap=cmap, levels=np.linspace(0, 160, 100)
        )
        cbar = plt.colorbar(contourf, label="Précipitations accumulées (mm/h)")
        cbar.set_ticks(np.linspace(0, 160, 8))
        axes.set_title(
            f"Simulation Méso-NH du {date} TU (DX = {resol_dx} m)\n"
            "Précipitation accumulées sur l'heure"
        )
        
        date = str(date).replace(":", "_")
        plt.savefig(f"acprr_hourly_{date}_{resol_dx}m.png")



if __name__ == "__main__":
    reader = get_mesonh(250)
    my_map = Map(reader.longitude + LON_OFFSET[250], reader.latitude + LAT_OFFSET[250])
    plot_precip_inprr(reader, my_map, resol_dx=250)

    # reader = get_mesonh(500)
    # my_map = Map(reader.longitude, reader.latitude)
    # plot_precip_acprr(reader, my_map, resol_dx=500)

    # reader = get_mesonh(1000)
    # my_map = Map(reader.longitude, reader.latitude)
    # plot_precip_acprr(reader, my_map, resol_dx=1000)
