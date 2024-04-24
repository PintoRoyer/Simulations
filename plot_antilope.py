#!/usr/bin/env python3
"""Some tests."""

from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import Antilope


files = [
    f"/home/roya/RADAR/NC/PRECIP_SOL_0_2208XX{str(time_index).zfill(2)}.nc"
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


antilope = Antilope(files, 17)
mymap = Map(antilope)
var_min, var_max = antilope.get_limits("prec")
levels = np.linspace(var_min, var_max, 100)

for i in range(23):
    plt.close("all")
    antilope.get_data(i)
    date = datetime.strptime(f"2022-08-01 {str(i).zfill(2)}:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(hours=int(antilope.data["time"][17]))

    axes = mymap.init_axes()[1]

    mymap.set_title(
        f"Précipitations mesurées par le réseau ANTILOPE\n{date} TU",
        fmt_kw={"date": date}
    )
    cf = mymap.plot_contourf("prec", cmap=cmap, levels=levels)
    plt.colorbar(cf, label="Précipitation (mm)", fraction=0.03)
    plt.tight_layout()
    plt.savefig(f"antilope_{date}.png")

for i in range(23):
    plt.close("all")
    antilope.get_data(i)
    date = datetime.strptime(f"2022-08-01 {str(i).zfill(2)}:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(hours=int(antilope.data["time"][17]))

    axes = mymap.init_axes()[1]
    axes.set_extent((
        2.5,
        antilope.longitude[-1],
        antilope.latitude[-1],
        45
    ))
    
    mymap.set_title(
        f"Précipitations mesurées par le réseau ANTILOPE\n{date} TU",
        fmt_kw={"date": date}
    )
    cf = mymap.plot_contourf("prec", cmap=cmap, levels=levels)
    plt.colorbar(cf, label="Précipitation (mm)", fraction=0.03)
    plt.tight_layout()
    plt.savefig(f"antilope_zoom_{date}.png")
