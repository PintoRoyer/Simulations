from plots import Map
from readers import MesoNH

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from datetime import datetime, timedelta


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 15
})


def get_index(var_array: np.array, value):
    min_delta = abs(value - var_array[0])
    index = 0
    for i in range(len(var_array)):
        if abs(value - var_array[i]) <= min_delta :
            min_delta = abs(value - var_array[i])
            index = i
    return index


def sum_clouds(thcw, thrw, thic, thsn, thgr):
    return thcw + thrw + thic + thsn + thgr


def norm_wind(um10, vm10, wind10):
    return um10 / wind10, vm10 / wind10 


def plot_zoom(mesonh, lon, lat, time, width):
    plt.close("all")
    
    # Limits
    lon_index = []
    lat_index = []
 
    for lim in lon:
        index = get_index(mesonh.longitude, lim)
        lon_index.append(index)
        
    for lim in lat:
        index = get_index(mesonh.latitude, lim)
        lat_index.append(index)

    # Creating Map instance
    my_map = Map(
        mesonh.longitude[lon_index[0]: lon_index[1]],
        mesonh.latitude[lat_index[0]: lat_index[1]]
    )
    
    # Pressure
    my_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"}
    )
    var = mesonh.get_var("MSLP")
    contourf = my_map.plot_contourf(
        var[lat_index[0]: lat_index[1], lon_index[0]: lon_index[1]],
        cmap="turbo",
        extend="both",
        levels=np.linspace(995, 1015, 100)
    )
    cb = plt.colorbar(contourf, label="Pression au niveau de la mer (hPa)")
    cb.set_ticks(np.linspace(995, 1015, 8))
    plt.savefig(f"pressure_{time}.png")
    
    # Clouds
    my_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"},
        feature_kw={"linewidth": 1, "alpha": 0.5, "color": "white"}
    )
    var = mesonh.get_var("THCW", "THRW", "THIC", "THSN", "THGR", func = sum_clouds)
    contourf = my_map.plot_contourf(
        var[lat_index[0]: lat_index[1], lon_index[0]: lon_index[1]],
        cmap=LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"]),
        levels=np.linspace(clouds_min, clouds_max, 100)
    )
    cb = plt.colorbar(contourf, label="Épaisseur nuageuse (mm)")
    cb.set_ticks(np.linspace(clouds_min, clouds_max, 8))
    plt.savefig(f"clouds_{time}.png")
    
    # Wind
    my_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})
    var = mesonh.get_var("WIND10", func = lambda x: x * 3.6)
    contourf = my_map.plot_contourf(
        var[lat_index[0]: lat_index[1], lon_index[0]: lon_index[1]],
        cmap=LinearSegmentedColormap.from_list("cmap2", ["white", (240/255, 248/255, 255/255), "darkcyan", "yellow", "orange", "red", "purple", "black"]), 
        levels=np.linspace(wind_min, wind_max, 100)
    )
    cb = plt.colorbar(contourf, label="Vitesse du vent horizontal (km/h)")
    cb.set_ticks(np.linspace(wind_min, wind_max, 8))

    wind_u, wind_v = mesonh.get_var("UM10", "VM10", "WIND10", func = norm_wind)
    my_map.plot_quiver(
        wind_u[lat_index[0]: lat_index[1], lon_index[0]: lon_index[1]],
        wind_v[lat_index[0]: lat_index[1], lon_index[0]: lon_index[1]], 
        x_mesh=50,
        y_mesh=50,
        width=width,
        scale=15,
        scale_units="xy",
        units="xy"
    )
    plt.savefig(f"wind_{time}.png")


def get_time_index(hour, minute):
    return (hour - 4) * 60 + (minute - 1)


files = []
for time_index in range (1, 361, 1):
    files.append(f"../Donnees/DX250/CORSE.1.SEG01.OUT.{str(time_index).zfill(3)}.nc")
mesonh = MesoNH(files)

clouds_min, clouds_max = mesonh.get_limits("THCW", "THRW", "THIC", "THSN", "THGR", func=sum_clouds)
wind_min, wind_max = mesonh.get_limits("WIND10", func=lambda x: x * 3.6)

args = (
    ((5.5, 7), (40, 43), 5, 0, 0.0075),
    ((6, 8), (40.5, 43), 6, 30, 0.0075),
    ((5.5, 8.5), (40.75, 43.5), 7, 0, 0.0075),
    ((6.5, 9), (41, 43.5), 7, 15, 0.0075),
    ((7, 9.5), (42, 43.8), 8, 15, 0.006),
    ((7, 10), (42.5, 43.8), 8, 45, 0.0065)   
)


for lon, lat, hour, minute, width in args[1:2]:
    mesonh.get_data(get_time_index(hour, minute))
    time = f"{str(hour).zfill(2)}h{str(minute).zfill(2)}"
    plot_zoom(mesonh, lon, lat, time, width)
