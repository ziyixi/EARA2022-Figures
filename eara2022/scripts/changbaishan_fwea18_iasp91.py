from .changbaishan_fwea18_base import plot_base
from functools import partial

conf = {
    'ref_key': "iasp91",
    'save_name': "changbaishan_fwea18_iasp91",
}

main = partial(plot_base, ref_key=conf['ref_key'], save_name=conf['save_name'])

if __name__ == "__main__":
    main()
