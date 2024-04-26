from plots import Map
from netCDF4 import Dataset
import matlplotlib.pyplot as plt

data = Dataset("/mesonh/bartc/corse_18aout22/prep_250m_from_mnh/001_prep_pgd/PGD_CORSE_0250M.nc")

my_map = Map(data.variables["longitude"][0], data.variables["latitude"][:, 0])
axes = my_map.init_axes()[1]
axes.set_extent([8.2, 9.8, 41.2, 43.1])
cf = my_map.plot_contourf(data.variables["ZS"], cmap="terrain")
plt.colorbar(cf, label="Altitude (m)")

plt.savefig("relief_250m.png")