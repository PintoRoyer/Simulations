from meso_nh import *

animation(
	250,
	clouds,
	"THCW", "THRW", "THIC", "THSN", "THGR",
	label="Épaisseur nuageuse (mm)",
	nlevels=100,
	feature_kw={"linewidth": 1, "alpha": 0.5, "color": "white"},
	func=sum_cloud
)
