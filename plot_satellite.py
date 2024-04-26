#!/usr/bin/env python3
"""Some tests."""

from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import Satellite


files = [
    f"/mesonh/bartc/corse_18aout22/satellite/merg_20220818{str(time_index).zfill(2)}_4km-pixel.nc4"
    for time_index in range(24)
]

sat = Satellite(files, 0)
mymap = Map(sat.longitude, sat.latitude)
time_ref = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

var_min, var_max = sat.get_limits("Tb")
levels = np.linspace(var_min, 250, 100)

for sat.time_step in range(2):
    for i in range(13):
        plt.close("all")
        sat.get_data(i)
        tb = sat.get_var("Tb")

        date = (
            time_ref + timedelta(days=float(sat.data["time"][sat.time_step]))
        ).strftime("%Y-%m-%d %H:%M")
    
        axes = mymap.init_axes(feature_kw={"color": "white"})[1]
        axes.set_extent((
            2.5,
            10.5,
            40,
            45    
        ))
        
        mymap.set_title(
            f"Mesure de température de brillance (satellite)\n{date} TU",
            fmt_kw={"date": date}
        )
        cf = mymap.plot_contourf(
            tb,
            cmap="",
            extend="max",
            levels=levels
        )
        plt.colorbar(cf, label="Température de brillance (K)", fraction=0.03)
        plt.tight_layout()
        plt.savefig(f"satellite_{date}.png")
