from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from plots import Map
from readers import MesoNH


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 15
})

cmap = LinearSegmentedColormap.from_list("cmap1", [
    "white",
    "blue",
    "cyan",
    "green",
    "yellow",
    "orange",
    "red",
    "purple",
    "black"
])
files = [
    f"../Donnees/DX250/CORSE.1.SEG01.OUT.{str(t).zfill(3)}.nc"
    for t in range(1, 361)
]
mesonh = MesoNH(files)
precip_map = Map(mesonh.longitude, mesonh.latitude)
var_min, var_max = np.inf, -np.inf

for hour in range(1, 361, 60):
    inprr = np.zeros(mesonh.longitude.shape)
    for time_index in range(hour, hour + 59):
        mesonh.get_data(time_index)
        inprr += mesonh.get_var("INPRR", func=lambda x: x * 60)
    
    if inprr.min() < var_min:
        var_min = inprr.min()
    if inprr.max() > var_max:
        var_max = inprr.max()

    date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(seconds=float(mesonh.data.variables["time"][0]))
    
    axes = precip_map.init_axes(fig_kw={"figsize": (8, 5), "layout": "compressed"})[1]
    cf = precip_map.plot_contourf(inprr * 1000, cmap=cmap, levels=np.linspace(0, 160, 100))
    cb = plt.colorbar(cf, label="Précipitations accumulées (mm)")
    cb.set_ticks(np.linspace(0, 160, 8))
    axes.set_title(f"Simulation Méso-NH du {date} TU (DX = 250 m)\nPrécipitation accumulées sur l'heure")
    
    # plt.show()
    plt.savefig(f"inprr_{date}.png")


with open("inprr_sum.json", "w") as file:
    file.write(f"{{\"inprr\" : [{var_min}, {var_max}]}}")
