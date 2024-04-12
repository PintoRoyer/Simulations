import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation
from netCDF4 import Dataset
from datetime import datetime, timedelta
import numpy as np


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 12
   })


PATH = "/mesonh/panf/ADASTRA/CORSE/DX250/"
TIME_REF = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S")
FILES = [
    f"{PATH}CORSE.1.SEG01.OUT.{str(time_index).zfill(3)}.nc"
    for time_index in range(1, 361, 1)
]


def get_limits(varname: str):
    """
    Search min and max of a given varname.
    
    Parameters
    ----------
    varname : str
        The name of the variable.
    
    Returns
    -------
    out : tuple
        A tuple containing two elements: (var_min, var_max).
    """
    var_min = np.inf
    var_max = - np.inf
    for filename in FILES:
        data = Dataset(filename)
        current_min = data.variables[varname][0].min()
        current_max = data.variables[varname][0].max()
        
        if current_min < var_min :
            var_min = current_min
            
        if current_max > var_max :
            var_max = current_max 
    
    return var_min, var_max


fig = plt.figure()
axes = plt.axes(projection=ccrs.PlateCarree())
axes.coastlines(linewidth=1, color="black", alpha=0.4)
axes.add_feature(cfeature.BORDERS, color="black", linewidth=1, alpha=0.4)

glines = axes.gridlines(draw_labels=True, linewidth=0.5)
glines.top_labels = glines.right_labels = False 

var_min, var_max = get_limits("ACPRR")
levels = np.linspace(var_min, var_max, 25)

frame = []
for filename in FILES:
    data = Dataset(filename)
    contourf = axes.contourf(
        data.variables["longitude"][0],
        data.variables["latitude"][:, 0],
        data.variables["ACPRR"][0],
        cmap="Blues",
        levels=levels 
    )
    date = TIME_REF + timedelta(seconds=int(data.variables["time"][0]))
    title = axes.text(0.5, 1.05, f"Simulation Méso-NH le {date} TU\n(dx = 250 m)", ha="center", transform=axes.transAxes)
    frame.append([contourf, title])

plt.colorbar(contourf, label="Taux de précipitations accumulées (mm)", format="%.0e", fraction=0.03)

animation = ArtistAnimation(fig, frame, interval=250)
animation.save("essai.mp4")
