from meso_nh import *

animation(
	250,
	wind,
	"WIND10",
	label="Vitesse du vent (km/h)",
	nlevels=100,
	feature_kw={"linewidth": 1, "alpha": 0.5, "color": "white"},
	func=from_ms_to_kmh
)
