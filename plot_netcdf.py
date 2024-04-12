from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import ArtistAnimation
from netCDF4 import Dataset

plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 12})


PATH = "../Donnees/DX250/"
TIME_REF = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S")
FILES = [
    f"{PATH}CORSE.1.SEG01.OUT.{str(time_index).zfill(3)}.nc" for time_index in range(1, 361, 10)
]


def norm(x, y):
    return np.sqrt(x**2 + y**2)


def get_limits(*varnames, func=lambda x: x):
    """
    Search min and max of a given varname.

    Parameters
    ----------
    function
        ...
    varnames : str
        The name of the variable.

    Returns
    -------
    out : tuple
        A tuple containing two elements: (var_min, var_max).
    """
    var_min = np.inf
    var_max = -np.inf
    for filename in FILES:
        data = Dataset(filename)

        args = [data.variables[varname][0] for varname in varnames]
        current_min = func(*args).min()
        current_max = func(*args).max()

        if current_min < var_min:
            var_min = current_min

        if current_max > var_max:
            var_max = current_max

    return var_min, var_max


fig = plt.figure(figsize=(10, 6))
axes = plt.axes(projection=ccrs.PlateCarree())
axes.coastlines(linewidth=1, color="black", alpha=0.4)
axes.add_feature(cfeature.BORDERS, color="black", linewidth=1, alpha=0.4)

glines = axes.gridlines(draw_labels=True, linewidth=0.5)
glines.top_labels = glines.right_labels = False

var_min, var_max = get_limits("UM10", "VM10", func=norm)
levels = np.linspace(var_min, var_max, 25)

frame = []
for filename in FILES:
    data = Dataset(filename)
    contourf = axes.contourf(
        data.variables["longitude"][0],
        data.variables["latitude"][:, 0],
        norm(data.variables["UM10"][0], data.variables["VM10"][0]),
        cmap="jet",
        levels=levels,
    )

    date = TIME_REF + timedelta(seconds=int(data.variables["time"][0]))
    title = axes.text(
        0.5,
        1.05,
        f"Simulation Méso-NH le {date} TU\n(dx = 250 m)",
        ha="center",
        transform=axes.transAxes,
    )
    frame.append([contourf, title])

plt.colorbar(contourf, label="Module de vent (m$\\cdot$s$ {-1}$)", format="%.0e", fraction=0.03)
plt.tight_layout()

animation = ArtistAnimation(fig, frame, interval=100)
animation.save("wind_10m.mp4")
animation.save("wind_10m.gif")
