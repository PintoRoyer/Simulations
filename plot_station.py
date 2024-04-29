import json
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from plots import TemporalProfile, get_index
from readers import MesoNH


def show_station(mesonh, lon, lat, name):
    plt.figure()
    axes = plt.axes(projection=ccrs.PlateCarree())
    axes.add_feature(cfeature.COASTLINE, linewidth=1, alpha=0.5)
    axes.add_feature(cfeature.BORDERS, linewidth=1, alpha=0.5)
    axes.set_extent((
        mesonh.longitude.min(),
        mesonh.longitude.max(),
        mesonh.latitude.min(),
        mesonh.latitude.max()
    ))

    glines = axes.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
    glines.top_labels = glines.right_labels = False

    axes.plot(lon, lat, ".", color="black", transform=ccrs.PlateCarree())
    axes.text(lon, lat, name.title(), color="black")


def get_mesonh(dx):
    files = [
        f"../Donnees/DX{dx}/CORSE.1.SEG01.OUT.{str(t).zfill(3)}.nc"
        for t in range(1, 361)    
    ]
    return MesoNH(files)


def get_wind10(lon, lat, dx):
    mesonh = get_mesonh(dx)
    i = get_index(mesonh.latitude, lat)[0]
    j = get_index(mesonh.longitude, lon)[1]

    wind10 = []
    for t in range(61, 361, 60):
        wind10.append(3.6 * mesonh.get_mean(i, j, "WIND10", t_range=range(t - 10, t + 1)))
    return wind10


def get_pressure(lon, lat, dx):
    mesonh = get_mesonh(dx)
    i = get_index(mesonh.latitude, lat)[0]
    j = get_index(mesonh.longitude, lon)[1]

    pressure = []
    for t in range(1, 361, 60):
        pressure.append(mesonh.get_mean(i, j, "MSLP", t_range=(t, )))
    return pressure


def plot_wind(name):
    with open(f"../Donnees/stations/stations.json", "r") as file:
        pos_stations = json.loads(file.read())
    lat, lon = pos_stations[name]

    show_station(get_mesonh(250), lon, lat, name)

    t_profile = TemporalProfile()

    for dx in (250, 500, 1000):
        t_profile.add_profile_from_array(
            range(5, 10),
            get_wind10(lon, lat, dx),
            label=f"Simulation\nDX = {dx} m"
        )

    t_profile.add_profile_from_csv(
        f"../Donnees/stations/{name}.csv",
        "heure",
        "vent",
        label=f"{name.title()}"
    )

    t_profile.axes.set_xlabel("Heure (TU)")
    t_profile.axes.set_ylabel("Vitesse du vent (km/h)")
    t_profile.axes.grid("on")

    plt.legend()
    plt.show()


def plot_pressure(name):
    with open(f"../Donnees/stations/stations.json", "r") as file:
        pos_stations = json.loads(file.read())
    lat, lon = pos_stations[name]

    show_station(get_mesonh(250), lon, lat, name)

    t_profile = TemporalProfile()

    for dx in (250, 500, 1000):
        t_profile.add_profile_from_array(
            range(4, 10),
            get_pressure(lon, lat, dx),
            label=f"Simulation\nDX = {dx} m"
        )

    t_profile.add_profile_from_csv(
        f"../Donnees/stations/{name}.csv",
        "heure",
        "pression",
        label=f"{name.title()}"
    )

    t_profile.axes.set_xlabel("Heure (TU)")
    t_profile.axes.set_ylabel("Pression (hPa)")
    t_profile.axes.grid("on")

    plt.legend()
    plt.show()

plot_pressure("cap corse")
