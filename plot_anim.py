import json


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs

from plots import Map
from readers import MesoNH, get_mesonh


with open("limits/lim_250m.json", "r", encoding="utf-8") as file:
    LIM = json.loads(file.read())


def sum_clouds(thcw, thrw, thic, thsn, thgr):
    """Add up different thickness of the condensed states of water."""
    return thcw + thrw + thic + thsn + thgr


def plot_frame_clouds(mesonh, my_map, index):
    # Clouds
    mesonh.get_data(index)
    my_map.init_axes(
        fig_kw={"figsize": (8, 5), "layout": "compressed"},
        feature_kw={"linewidth": 1, "alpha": 0.5, "color": "white"},
    )
    var = mesonh.get_var("THCW", "THRW", "THIC", "THSN", "THGR", func=sum_clouds)
    contourf = my_map.plot_contourf(
        var,
        cmap=LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"]),
        levels=np.linspace(LIM["clouds"][0], LIM["clouds"][1], 100),
    )
    cbar = plt.colorbar(contourf, label="Épaisseur nuageuse (mm)")
    cbar.set_ticks(np.linspace(LIM["clouds"][0], LIM["clouds"][1], 8))

    plt.savefig(f"clouds_{index}.png")



mesonh = get_mesonh(250)
my_map = Map(mesonh.longitude, mesonh.latitude)
for i in range(186, 361, 5):
    plt.close("all")
    plot_frame_clouds(mesonh, my_map, i)
