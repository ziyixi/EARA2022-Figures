from .geo_map import main as geo_map_main
from .event_station_distribution import main as event_station_distribution_main
from .misfit import main as misfit_main
from .hist import main as hist_main
from .psf import main as psf_main
from .waveform import main as waveform_main
from .vs import main as vs_main
from .vp import main as vp_main
from .vp_vs import main as vp_vs_main
from .radial import main as radial_main
from .slab_vs import main as slab_main_vs
from .slab_vp import main as slab_main_vp
from .changbaishan_models_stw105_vs import main as changbaishan_models_stw105_vs_main
from .changbaishan_models_stw105_vp import main as changbaishan_models_stw105_vp_main
from .changbaishan_models_eara2022_vs import main as changbaishan_models_eara2022_vs_main
from .changbaishan_models_eara2022_vp import main as changbaishan_models_eara2022_vp_main
from .changbaishan_models_ak135_vs import main as changbaishan_models_ak135_vs_main
from .changbaishan_models_ak135_vp import main as changbaishan_models_ak135_vp_main
from .con_vs import main as con_vs_main
from .con_vp import main as con_vp_main
from .vol_vs import main as vol_vs_main
from .vol_vp import main as vol_vp_main

__all__ = [
    'geo_map_main',
    'event_station_distribution_main',
    'misfit_main',
    'hist_main',
    'psf_main',
    'waveform_main',
    'vs_main',
    'vp_main',
    'vp_vs_main',
    'radial_main',
    'slab_main_vs',
    'slab_main_vp',
    'changbaishan_models_stw105_vs_main',
    'changbaishan_models_stw105_vp_main',
    'changbaishan_models_eara2022_vs_main',
    'changbaishan_models_eara2022_vp_main',
    'changbaishan_models_ak135_vs_main',
    'changbaishan_models_ak135_vp_main',
    'con_vs_main',
    'con_vp_main',
    'vol_vs_main',
    'vol_vp_main'
]
