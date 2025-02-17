""" 
vp_ak135.py

plot the horizontal crosssection of the model.
"""
from functools import partial

import numpy as np

from .vpvs_base import plot_base

conf = {
    'model_type': "vp",
    'depths': np.arange(100, 1000, 100),
    'cpt_series': "-0.06/0.06/0.01",
    'cpt_reverse': False,
    'save_name': "vp_ak135",
    'colorbar_content': "@~d@~lnVp(%)",
    'ref': 'ak135'
}

main = partial(plot_base, model_type=conf['model_type'], depths=conf['depths'], cpt_series=conf['cpt_series'],
               cpt_reverse=conf['cpt_reverse'], save_name=conf['save_name'], colorbar_content=conf['colorbar_content'], ref=conf['ref'])

if __name__ == "__main__":
    main()
