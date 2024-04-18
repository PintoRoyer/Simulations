from meso_nh import *


animation(
	250,
	pressure,
	"MSLP",
	label="Pression (hPa)",
	nlevels=np.linspace(996, 1023, 100)
)
