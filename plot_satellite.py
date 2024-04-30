#!/usr/bin/env python3
"""Plot satellite data."""

from datetime import datetime, timedelta
from threading import Thread
import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from plots import Map
from readers import Satellite


logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)

files = [
    f"../Donnees/satellite/merg_20220818{str(time_index).zfill(2)}_4km-pixel.nc4"
    for time_index in range(24)
]

cmap = LinearSegmentedColormap.from_list("",[
    (0.0, "purple"),
    (0.1, "blue"),
    (0.2, "cyan"),
    (0.3, "lime"),
    (0.4, "green"),
    (0.5, "white"),
    (1.0, "black"),

])


def plot_sat(sat):
    plt.close("all")
    logging.info(f"plot_sat: starting")
    mymap = Map(sat.longitude, sat.latitude)
    tb = sat.get_var("Tb")

    date = (
        datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        + timedelta(days=float(sat.get_var("time")))
    ).strftime("%Y-%m-%d %H:%M")
    
    logging.info(f".. Map: creation")
    axes = mymap.init_axes(feature_kw={"color": "white"})[1]
    axes.set_extent((
        2.5,
        10.5,
        40,
        45    
    ))
    
    logging.info(f".. Map: title")
    mymap.set_title(
        f"Mesure de température de brillance (satellite)\n{date} TU",
        fmt_kw={"date": date}
    )
    
    logging.info(f".. Map: contourf")
    cf = mymap.plot_contourf(
        tb,
        cmap=cmap,
        extend="min",
        norm=TwoSlopeNorm(235),
        levels=levels
    )
    
    logging.info(f".. Map: colorbar")
    plt.colorbar(cf, label="Température de brillance (K)", fraction=0.03)
    
    logging.info(f"..pyplot: savefig")
    plt.tight_layout()
    plt.savefig(f"satellite_{date}.png")
    logging.info(f"plot_sat: ending")


sat = Satellite(files, 0)
var_min, var_max = sat.get_limits("Tb")
levels = np.linspace(210, var_max, 100)

for sat.time_step in range(2):
    for i in range(13):
        sat.get_data(i)
        plot_sat(sat)
