""" 
slab_vp_eara2022.py

Plot the slab vertical cross-secations.
"""
from functools import partial

from .slab_base import slab_plot_base

# * configuration for the plotting
conf = {
    "x_offset": 7.7,
    "y_offset": 5.9,
    "yabs_offset": 3,
    "ytopo_offset": 4,
    'parameter': 'vp',
    'cbar': 'Vp',
    'length': 25,
    'abs_cpt': '6.2/8.7/0.5',
    'save_name': "slab_vp_eara2022",
    'x_fig': 7.5,
    'ref': 'eara2022',
}

main = partial(slab_plot_base, conf=conf)
