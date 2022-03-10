""" 
cache.py

disk caching for the result of expensive numpy functions
"""
from eara2022 import resource
import numpy as np
from os.path import isfile
from typing import Optional


def save_cache(file_name: str, content: np.ndarray) -> None:
    # name should have .npy
    cache_path = resource(['cache', file_name+".npy"],
                          normal_path=True, check=False)
    np.save(arr=content, file=cache_path)


def load_cache(file_name: str) -> Optional[np.ndarray]:
    cache_path = resource(['cache', file_name+".npy"],
                          normal_path=True, check=False)
    if isfile(cache_path):
        res = np.load(cache_path)
        return res
    else:
        return None
