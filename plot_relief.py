"""
Corsica's relief
================

Description
-----------
Draw Corsica relief at DX = 250m on a map and export fig in a PNG file.
"""

import matplotlib.pyplot as plt
from netCDF4 import Dataset

from plots import Map

# Open PGD data
data = Dataset("/mesonh/bartc/corse_18aout22/prep_250m_from_mnh/001_prep_pgd/PGD_CORSE_0250M.nc")

# Create a new map and set extent
my_map = Map(data.variables["longitude"][:, :], data.variables["latitude"][:, :])
axes = my_map.init_axes()[1]
axes.set_extent([8.2, 9.8, 41.2, 43.1])

# Add contourf and colorbar
contourf = my_map.plot_contourf(data.variables["ZS"], cmap="terrain")
plt.colorbar(contourf, label="Altitude (m)")

# Export figure
plt.savefig("relief_250m.png")
