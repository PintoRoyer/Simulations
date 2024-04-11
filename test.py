import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.animation import ArtistAnimation

data = xr.open_mfdataset("../Données/DX250/CORSE.1.SEG01.OUT.*.nc")

fig = plt.figure()
axes = plt.axes(projection=ccrs.PlateCarree())
axes.coastlines(linewidth=1, color="black", alpha=0.4)
axes.add_feature(cfeature.BORDERS, color="black", linewidth=1, alpha=0.4)

glines = axes.gridlines(draw_labels=True, linewidth=0.5)
glines.top_labels = glines.right_labels = False

levels = np.linspace(data.ACPRR.min(), data.ACPRR.max(), 25)

frame = []

for time in range(data.ACPRR.shape[0]):
    n = int(time * 50 / data.ACPRR.shape[0])
    print("[" + n * "#" + (50 - n) * " " + "]", end="\r")
    contourf = axes.contourf(
        data.longitude[0], data.latitude[:, 0], data.ACPRR[time], cmap="Blues", levels=levels
    )
    date, hour = str(data.time[time].values).split("T")
    title = axes.text(
        0.5,
        1.05,
        f"Simulation Méso-NH le {date} à {hour[: 5]} TU\n(dx = 250 m)",
        ha="center",
        transform=axes.transAxes,
    )
    frame.append([contourf, title])


plt.colorbar(contourf, label="Taux de précipitations accumulées (mm)", format="%.0e", fraction=0.03)

animation = ArtistAnimation(fig, frame, interval=250)

animation.save("essai.gif")

plt.show()
