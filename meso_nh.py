import plots

from datetime import datetime, timedelta

import numpy as np

from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature

import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation
from matplotlib.colors import LinearSegmentedColormap


# plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 12})


def from_ms_to_kmh(x):
    """Convert the given variable from m/s to km/h."""
    return x * 3.6


def from_m_to_mm(x):
    """Convert the given variable from m to mm."""
    return x * 1e3


def sum_cloud(cw, rw, ic, sn, gr):
    """Add up the different thickness to get the cloud thickness."""
    return cw + rw + ic + sn + gr


def normalize(wind_u, wind_v, wind_spd):
    return 2 * wind_u / wind_spd, 2 * wind_v / wind_spd
    


# WIND10 : [contourf + quiver]           "jet" 
# ACPRR  : [contourf + pression contour] LinearSegmentedColormap.from_list("cmap1", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"])
# INPRR  : [contourf + pression contour] LinearSegmentedColormap.from_list("cmap1", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"])
# MSLP   : [contour]                     "jet", "turbo"
# clouds : [contourf + pression contour] LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"]), feature_kw{"linewidth": 1, "alpha": 0.5, "color": "white"}


def clouds_pressure(data, date, dx, levels, axes=None, isanimated=False):
	if not axes:
		fig, axes, glines = plots.init_axes(feature_kw={"linewidth": 1, "alpha": 0.5, "color": "white"})

	contour = plots.plot_contour(axes, data, "MSLP", colors="gray", levels=10, alpha=0.75)
	plt.clabel(contour, contour.levels, inline=True, colors="gray", fontsize=8)

	contourf = plots.plot_contourf(
		axes,
		data,
		"THCW", "THRW", "THIC", "THSN", "THGR", 
		func=sum_cloud,
		cmap=LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"]),
		levels=levels
	)
	title = plots.set_title(axes, "Simulation Méso-NH du {date} (DX = {dx})\nCouverture nuageuse et isobares", fmt_kw={"date": date, "dx": dx})
	
	if isanimated:
		return [contourf, contour, title]

	plt.colorbar(contourf, label="Épaisseur nuageuse (mm)", fraction=0.03)
	plt.tight_layout()
	plt.savefig(f"cloud_pressure_{date}_DX{dx}.png")


def clouds(data, date, dx, levels, axes=None, isanimated=False):
	if not axes:
		fig, axes, glines = plots.init_axes(feature_kw={"linewidth": 1, "alpha": 0.5, "color": "white"})
	
	contourf = plots.plot_contourf(
		axes,
		data,
		"THCW", "THRW", "THIC", "THSN", "THGR", 
		func=sum_cloud,
		cmap=LinearSegmentedColormap.from_list("cmap2", ["black", "white", "blue", "red"]),
		levels=levels
	)
	title = plots.set_title(axes, "Simulation Méso-NH du {date} (DX = {dx})\nCouverture nuageuse", fmt_kw={"date": date, "dx": dx})
	
	if isanimated:
		return [contourf, title]
	
	plt.colorbar(contourf, label="Épaisseur nuageuse (mm)", fraction=0.03)
	plt.tight_layout()
	plt.savefig(f"cloud_{date}_DX{dx}.png")


def wind(data, date, dx, levels, axes=None, isanimated=False):
	if not axes:
		fig, axes, glines = plots.init_axes(feature_kw={"linewidth": 1, "alpha": 0.75, "color": "white"})
	
	contourf = plots.plot_contourf(
		axes,
		data,
		"WIND10",
		func=from_ms_to_kmh,
		cmap="jet",
		levels=levels
	)
	quiver = plots.plot_quiver(axes, data, "UM10", "VM10", "WIND10", mesh=25, func=normalize)
	title = plots.set_title(axes, "Simulation Méso-NH du {date} (DX = {dx})\nModule et direction du vent à 10 m", fmt_kw={"date": date, "dx": dx})

	if isanimated:
		return [contourf, quiver, title]

	plt.colorbar(contourf, label="Vitesse du vent (km/h)", fraction=0.03)
	plt.tight_layout()
	plt.savefig(f"wind_{date}_DX{dx}.png")


def instant_precipitation(data, date, dx, levels, axes=None, isanimated=False):
	if not axes:
		fig, axes, glines = plots.init_axes()
	
	contourf = plots.plot_contourf(
		axes,
		data,
		"INPRR",
		func=from_m_to_mm,
		cmap=LinearSegmentedColormap.from_list("cmap1", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"]),
		levels=levels
	)
	title = plots.set_title(axes, "Simulation Méso-NH du {date} (DX = {dx})\nTaux de précipitation instantané", fmt_kw={"date": date, "dx": dx})
	
	if isanimated:
		return [contourf, title]

	plt.colorbar(contourf, label="Taux de précipitation (mm/s)", fraction=0.03)
	plt.tight_layout()
	plt.savefig(f"inprr_{date}_DX{dx}.png")


def accumulated_precipitation(data, date, dx, levels, axes=None, isanimated=False):
	if not axes:	
		fig, axes, glines = plots.init_axes()
	
	contourf = plots.plot_contourf(
		axes,
		data,
		"ACPRR",
		func=from_m_to_mm,
		cmap=LinearSegmentedColormap.from_list("cmap1", ["white", "blue", "cyan", "green", "yellow", "orange", "red", "purple", "black"]),
		levels=levels
	)
	title = plots.set_title(axes, "Simulation Méso-NH du {date} (DX = {dx})\nPrécipitations accumulées", fmt_kw={"date": date, "dx": dx})

	if isanimated:
		return [contourf, title]

	plt.colorbar(contourf, label="Précipitations accumulées (mm)", fraction=0.03)
	plt.tight_layout()
	plt.savefig(f"acprr_{date}_DX{dx}.png")


def pressure(data, date, dx, levels, axes=None, isanimated=False):
	if not axes:
		fig, axes, glines = plots.init_axes()
	
	contourf = plots.plot_contourf(
		axes,
		data,
		"MSLP",
		cmap="turbo",
		levels=levels
	)
	title = plots.set_title(axes, "Simulation Méso-NH du {date} (DX = {dx})\nPression au niveau de la mer", fmt_kw={"date": date, "dx": dx})
	
	if isanimated:
		return [contourf, title]
	
	plt.colorbar(contourf, label="Pression (hPa)", fraction=0.03)
	plt.tight_layout()
	plt.savefig(f"pressure_{date}_DX{dx}.png")


def get_levels(files, nlevels, *varnames, func=lambda x: x):
	if isinstance(nlevels, int):
		var_min, var_max = plots.get_limits(files, *varnames, func=func)
		return np.linspace(var_min, var_max, nlevels)
	return nlevels


	
def animation(dx, animate_func, *varnames, label, nlevels, feature_kw=None, func=lambda x: x):
	files = [
		f"/mesonh/panf/ADASTRA/CORSE/DX{dx}/CORSE.1.SEG01.OUT.{str(time_index).zfill(3)}.nc"
		for time_index in range(1, 361, 2)
	]
	
	levels = get_levels(files, nlevels, *varnames, func=func)

	fig, axes, glines = plots.init_axes(feature_kw=feature_kw)
	frame = []
	
	for filename in files:
		data = Dataset(filename)
		date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(seconds=int(data.variables["time"][0]))

		frame.append(animate_func(
            data=data,
            date=date,
            dx=dx,
            levels=levels,
            axes=axes,
            isanimated=True
        ))
	
	plt.colorbar(frame[-1][0], label=label, fraction=0.03)
	plt.tight_layout()

	animation = ArtistAnimation(fig, frame, interval=100)
	animation.save(f"{animate_func.__name__}.gif")



data = Dataset("/mesonh/panf/ADASTRA/CORSE/DX250/CORSE.1.SEG01.OUT.360.nc")
date = datetime.strptime("2022-08-18 00:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(seconds=int(data.variables["time"][0]))
contourf = accumulated_precipitation(data, date, 250, levels=100)[0]
plt.colobar(contourf, label="Précipitation accumulées (mm)", fraction=0.03)
plt.tight_layout()
plt.savefig("precip_accumulees.png")
