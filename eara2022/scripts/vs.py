""" 
vs.py

plot the horizontal crosssection of the model.
"""
from .utils.vpvs_base import plot_base
from functools import partial
import numpy as np

conf = {
    'model_type': "vs",
    'depths': np.arange(100, 1000, 100),
    'cpt_series': "-0.06/0.06/0.01",
    'cpt_reverse': False,
    'save_name': "vs.pdf",
    'colorbar_content': "@~d@~lnVs(%)"
}

main = partial(plot_base, model_type=conf['model_type'], depths=conf['depths'], cpt_series=conf['cpt_series'],
               cpt_reverse=conf['cpt_reverse'], save_name=conf['save_name'], colorbar_content=conf['colorbar_content'])

if __name__ == "__main__":
    main()
