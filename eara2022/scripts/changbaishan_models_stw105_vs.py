"""
changbaishan_models_stw105_vs.py

plot the model comparision figure with stw105 and vs.
"""
from .changbaishan_models_base import plot_base
from functools import partial

conf = {
    'parameter': "vs",
    'ref_key': "stw105",
    'save_name': "changbaishan_models_stw105_vs",
    'colorbar_content': "@~d@~lnV(%)",
}

main = partial(plot_base, parameter=conf['parameter'],
               ref_key=conf['ref_key'], save_name=conf['save_name'], colorbar_content=conf['colorbar_content'])

if __name__ == "__main__":
    main()
