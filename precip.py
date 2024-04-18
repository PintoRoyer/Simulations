from meso_nh import *

animation(
	250,
 	instant_precipitation,
	"INPRR",
	label="Taux de précipitation (mm/s)",
	nlevels=100,
	func=from_m_to_mm
)
