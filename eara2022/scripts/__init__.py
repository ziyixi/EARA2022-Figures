from .geo_map import main as geo_map_main
from .event_station_distribution import main as event_station_distribution_main
from .misfit import main as misfit_main
from .hist import main as hist_main
from .psf import main as psf_main
from .waveform import main as waveform_main
from .vs import main as vs_main
from .vp import main as vp_main

__all__ = [
    'geo_map_main',
    'event_station_distribution_main',
    'misfit_main',
    'hist_main',
    'psf_main',
    'waveform_main',
    'vs_main',
    'vp_main'
]
