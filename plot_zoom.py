#! /usr/bin/env python3
"""Plot zoom of clouds, pressure and wind for the different resolution of the simulation."""

import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs

from plots import Map
from readers import MesoNH, get_mesonh, index_to_lonlat, lonlat_to_index, get_time_index
from plot_station import all_stations_on_axes


plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 15})


def sum_clouds(thcw, thrw, thic, thsn, thgr):
    """Add up different thickness of the condensed states of water."""
    return thcw + thrw + thic + thsn + thgr


def norm_wind(um10, vm10, wind10):
    """Normalize the wind components."""
    return um10 / wind10, vm10 / wind10


def plot_zoom(mesonh: MesoNH, i_lim: tuple, j_lim: tuple, time: str, resol_dx: int):
    """
    Plot zoomed-in maps for clouds, pressure and wind at a given resolution.

    Parameters
    ----------
    mesonh : MesoNH
        A Meso-NH reader instance.
    i_lim : tuple
        The limit indexes on x-axis.
    j_lim : tuple
        The limit indexes on y-axis.
    time : str
        The time in a string. It's only use for display.
    resol_dx : int
        The desired resolution.
    """
    plt.close("all")

    # Creating Map instance
    my_map = Map(mesonh.longitude, mesonh.latitude)

    # Information on zoom
    lon = [0, 0]  # bornes min max lon
    lat = [0, 0]  # bornes min max lat
    lon[0], lat[0] = index_to_lonlat(mesonh, i_lim[0], j_lim[0])
    lon[1], lat[1] = index_to_lonlat(mesonh, i_lim[1], j_lim[1])
    print(f"{time}\n" + len(time) * "-")
    print("Longitude")
    print(f".. {(lon[0]), lon[1]}°E")
    print(f".. {i_lim}")
    print(f".. {(i_lim[1] - i_lim[0]) * resol_dx / 1e3} km")
    print("Latitude")
    print(f".. {(lat[0]), lat[1]}°E")
    print(f".. {j_lim}")
    print(f".. {(j_lim[1] - j_lim[0]) * resol_dx / 1e3} km\n")

    zoom = (
        f"{round(float(lat[0]), 1)}-{round(float(lat[1]), 1)}N"
        f"_{round(float(lon[0]), 1)}-{round(float(lon[1]), 1)}E"
    )

    # Limits for colorbars
    with open("limits/lim_250m.json", "r", encoding="utf-8") as file:
        lim = json.loads(file.read())

    # Pressure
    axes = my_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]
    axes.set_extent([lon[0], lon[1], lat[0], lat[1]])

    var = mesonh.get_var("MSLP")
    contourf = my_map.plot_contourf(
        var, cmap="turbo", extend="both", levels=np.linspace(995, 1015, 100)
    )
    cbar = plt.colorbar(contourf, label="Pression au niveau de la mer (hPa)")
    cbar.set_ticks(np.linspace(995, 1015, 8))
    plt.savefig(f"pressure_{time}_{zoom}_{resol_dx}m.png")

    # Clouds
    axes = my_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"},
        feature_kw={"linewidth": 1, "alpha": 0.5, "color": "white"},
    )[1]
    axes.set_extent([lon[0], lon[1], lat[0], lat[1]])

    var = mesonh.get_var("THCW", "THRW", "THIC", "THSN", "THGR", func=sum_clouds)
    contourf = my_map.plot_contourf(
        var,
        cmap=LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"]),
        levels=np.linspace(lim["clouds"][0], lim["clouds"][1], 100),
    )
    cbar = plt.colorbar(contourf, label="Épaisseur nuageuse (mm)")
    cbar.set_ticks(np.linspace(lim["clouds"][0], lim["clouds"][1], 8))
    plt.savefig(f"clouds_{time}_{zoom}_{resol_dx}m.png")

    # Wind speed
    axes = my_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"},
        feature_kw={"color": "black"}
    )[1]
    axes.set_extent([lon[0], lon[1], lat[0], lat[1]])
    var = mesonh.get_var("WIND10", func=lambda x: x * 3.6)
    contourf = my_map.plot_contourf(
        var,
        cmap=LinearSegmentedColormap.from_list(
            "cmap2",
            [
                "white",
                (240 / 255, 248 / 255, 255 / 255),
                "darkcyan",
                "yellow",
                "orange",
                "red",
                "purple",
                "black",
            ],
        ),
        levels=np.linspace(lim["wind"][0], lim["wind"][1], 100),
    )
    cbar = plt.colorbar(contourf, label="Vitesse du vent horizontal (km/h)")
    cbar.set_ticks(np.linspace(lim["wind"][0], lim["wind"][1], 8))

    # Wind direction
    if i_lim == (0, -1):
        kwargs = {"scale" : 40}
            
    else:
        mesh = 25
        if resol_dx == 500:
            mesh = 12
        elif resol_dx == 1000:
            mesh = 6
        kwargs = {
            "x_mesh": mesh,
            "y_mesh": mesh,
            "width": 0.005,
            "scale": 20,
            "scale_units": "xy",
            "units": "xy"
        }

    wind_u, wind_v = mesonh.get_var("UM10", "VM10", "WIND10", func=norm_wind)
    my_map.plot_quiver(
        wind_u,
        wind_v,
        **kwargs
    )
    plt.savefig(f"wind_{time}_{zoom}_{resol_dx}m.png")


def plot_zoom_on_axes(lon, lat, hour, minute):
    plt.close("all")
    time = f"{str(hour).zfill(2)}h{str(minute).zfill(2)}"

    # Creating Map instance
    mesonh = get_mesonh(250)
    my_map = Map(mesonh.longitude, mesonh.latitude)


    zoom = (
        f"{round(float(lat[0]), 1)}-{round(float(lat[1]), 1)}N"
        f"_{round(float(lon[0]), 1)}-{round(float(lon[1]), 1)}E"
    )

    # Limits for colorbars
    with open("limits/lim_250m.json", "r", encoding="utf-8") as file:
        lim = json.loads(file.read())


    # clouds
    fig, axes = plt.subplots(1, 3, figsize=(24, 5), layout="compressed", subplot_kw={"projection": ccrs.PlateCarree()})


    
    for index, resol_dx in enumerate((250, 500, 1000)):
        geoaxes = my_map.init_axes(
            axes[index],
            feature_kw={"color": "black"}
        )[1]
        geoaxes.set_extent([lon[0], lon[1], lat[0], lat[1]])
        geoaxes.set_title(f"DX = {resol_dx} m")

        mesonh = get_mesonh(resol_dx)
        mesonh.get_data(get_time_index(hour, minute))
        my_map.longitude = mesonh.longitude
        my_map.latitude = mesonh.latitude

        axes[index].set_extent([lon[0], lon[1], lat[0], lat[1]])
        var = mesonh.get_var("WIND10", func=lambda x: x * 3.6)
        contourf = my_map.plot_contourf(
            var,
            cmap=LinearSegmentedColormap.from_list(
                "cmap2",
                [
                    "white",
                    (240 / 255, 248 / 255, 255 / 255),
                    "darkcyan",
                    "yellow",
                    "orange",
                    "red",
                    "purple",
                    "black",
                ],
            ),
            levels=np.linspace(lim["wind"][0], lim["wind"][1], 100),
        )

        # Wind direction
        if i_lim == (0, -1):
            kwargs = {"scale" : 40}
                
        else:
            mesh = 25
            if resol_dx == 500:
                mesh = 12
            elif resol_dx == 1000:
                mesh = 6
            kwargs = {
                "x_mesh": mesh,
                "y_mesh": mesh,
                "width": 0.005,
                "scale": 20,
                "scale_units": "xy",
                "units": "xy"
            }

        wind_u, wind_v = mesonh.get_var("UM10", "VM10", "WIND10", func=norm_wind)
        my_map.plot_quiver(
            wind_u,
            wind_v,
            **kwargs
        )

    cbar = plt.colorbar(contourf, label="Vitesse du vent horizontal (km/h)")
    cbar.set_ticks(np.linspace(lim["wind"][0], lim["wind"][1], 8))

    plt.show()
    # plt.savefig(f"wind_{time}_{zoom}.png")


def latex_code(mesonh: MesoNH, i_lim: tuple, j_lim: tuple, time: str, resol_dx: int):
    """
    Generate and print LaTeX code that contains a tabular with the given index, the limit
    coordinates and size of the zoom.

    Parameters
    ----------
    mesonh : MesoNH
        A Meso-NH reader instance.
    i_lim : tuple
        The limit indexes on x-axis.
    j_lim : tuple
        The limit indexes on y-axis.
    time : str
        The time in a string. It's only use for display.
    resol_dx : int
        The desired resolution.
    """
    lon = mesonh.longitude
    lat = mesonh.latitude

    content = "\\begin{center} \\begin{tabular}{rl}"
    content += f"\n\t\\textbf{{Heure simulation}}    & {time} TU \\\\"
    content += "\n\t\\textbf{Heure observation}   & \\\\"
    content += (
        f"\n\t\\textbf{{Longitude}}           & {lon[j_lim[0], i_lim[0]]:.5f}°E"
        f" -- {lon[j_lim[1], i_lim[1]]:.5f}°E \\\\"
    )
    content += f"\n\t\\textbf{{Index longitude}}     & {i_lim[0]} -- {i_lim[1]} \\\\"
    content += (
        f"\n\t\\textbf{{Distance zonale}}     & {(i_lim[1] - i_lim[0]) * resol_dx/1000}~km \\\\"
    )
    content += (
        f"\n\t\\textbf{{Latitude}}            & {lat[j_lim[0], i_lim[0]]:.5f}°N"
        f" -- {lat[j_lim[1], i_lim[1]]:.5f}°N \\\\"
    )
    content += f"\n\t\\textbf{{Index latitude}}      & {j_lim[0]} -- {j_lim[1]} \\\\"
    content += (
        f"\n\t\\textbf{{Distance méridienne}} & {(j_lim[1] - j_lim[0]) * resol_dx/1000}~km \\\\"
    )
    content += "\n\\end{tabular} \\end{center}"

    print(content)


def run_all(resol_dx, args, *, plot: bool = False, latex: bool = False):
    """
    Run ``plot_zoom`` and ``latex_code`` from a list of pre-defined zooms.

    Parameters
    ----------
    resol_dx : int
        The resolution of the simulation.
    args : iterable
        The arguments to be given to ``plot_all`` it should be like:

            args = (
                ((i_min, i_max), (j_min, j_max), hour, minute),
            )

    plot : bool, keyword-only, optionnal
        If set on ``True`` ``plot_zoom`` will be called. By default on ``False``.
    latex : bool, keyword-only, optionnal
        If set on ``True`` ``latex_code`` will be called. By default on ``False``.

    """
    mesonh = get_mesonh(resol_dx)

    for i_lim, j_lim, hour, minute in args:
        mesonh.get_data(get_time_index(hour, minute))
        time = f"{str(hour).zfill(2)}h{str(minute).zfill(2)}"

        if plot:
            plot_zoom(mesonh, i_lim, j_lim, time, resol_dx)
        if latex:
            latex_code(mesonh, i_lim, j_lim, time, resol_dx)


if __name__ == "__main__":
    dx250_zoom = (
        ((600, 860), (497, 1397), 5, 0),
        ((950, 1250), (966, 1400), 6, 30),
        ((1000, 1370), (1200, 1500), 7, 0),
        ((1150, 1450), (1260, 1530), 7, 15),
        ((1440, 1790), (1530, 1730), 8, 15),
        ((1470, 1940), (1650, 1930), 8, 45),
    )
    
    dx500_zoom = (
        ((304 , 434), (244 , 694), 5, 0),
        ((490 , 615), (519 , 688), 6, 30),
        ((490 , 688), (604 , 770), 7, 0),
        ((578 , 728), (615 , 752), 7, 15),
        ((670 , 896), (769 , 869), 8, 15),
        ((718 , 970), (790 , 960), 8, 45),
    )

    dx1000_zoom = (
        ((148, 215), (123, 348), 5, 0),
        ((230, 312), (242, 362), 6, 30),
        ((247, 342), (298, 381), 7, 0),
        ((275, 363), (314, 389), 7, 15),
        ((320, 446), (377, 453), 8, 15),
        ((383, 483), (414, 472), 8, 45),
    )

    no_zoom = (
        ((0, -1), (0, -1), 5, 0),
        ((0, -1), (0, -1), 6, 30),
        ((0, -1), (0, -1), 7, 0),
        ((0, -1), (0, -1), 7, 15),
        ((0, -1), (0, -1), 8, 15),
        ((0, -1), (0, -1), 8, 45),
    )

    time_index = 2

    zooms = (dx250_zoom, dx500_zoom, dx1000_zoom)
    lon_min = []
    lon_max = []
    lat_min = []
    lat_max = []

    for index, value in enumerate((250, 500, 1000)):
        mesonh = get_mesonh(value)
        i_lim, j_lim, hour, minute = zooms[index][time_index]
        
        tmp = index_to_lonlat(mesonh, i_lim[0], j_lim[0])
        lon_min.append(tmp[0])
        lat_min.append(tmp[1])

        tmp = index_to_lonlat(mesonh, i_lim[1], j_lim[1])
        lon_max.append(tmp[0])
        lat_max.append(tmp[1])

    lon = [min(lon_min), max(lon_max)]
    lat = [min(lat_min), max(lat_max)]
    print(lon, lat)
    plot_zoom_on_axes(lon, lat, hour, minute)
        

    # mesonh250 = get_mesonh(250)
    # mesonh500 = get_mesonh(500)
    # mesonh1000 = get_mesonh(1000)
    # lon_lim, lat_lim = index_to_lonlat(mesonh1000, (383, 483), (414, 472))
    # i_lim, j_lim = lonlat_to_index(mesonh500, lon_lim, lat_lim)
    # print(i_lim, j_lim)
