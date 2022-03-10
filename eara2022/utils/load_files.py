import pickle
import seisflow


def load_pickle(pickle_path: str):
    # might load windows, so we import seisflow here to ensure the installiation
    with open(pickle_path, "rb") as f:
        data = pickle.load(f)
    return data
