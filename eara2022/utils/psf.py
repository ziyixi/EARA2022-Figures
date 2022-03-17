""" 
psf.py

handle the point spread function related problems.
"""
import numpy as np
import xarray as xr
from numba import float64, guvectorize, njit, prange

from .cache import load_cache, save_cache

MODEL_SHAPE = (421, 281, 201)


@guvectorize([(float64[:], float64[:], float64[:], float64[:], float64[:], float64[:])], "(n),(n),(n)->(n),(n),(n)", nopython=True)
def latlondep2xyz_sphere(lat: np.ndarray, lon: np.ndarray, dep: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray):
    # coordinate conversion
    for index in range(len(lat)):
        r = (6371. - dep[index]) / 6371.
        theta = 90-lat[index]
        phi = lon[index]
        z[index] = r * np.cos(np.deg2rad(theta))
        h = r * np.sin(np.deg2rad(theta))
        x[index] = h * np.cos(np.deg2rad(phi))
        y[index] = h * np.sin(np.deg2rad(phi))


@njit(parallel=True)
def get_per(per_array: np.ndarray, psf_list: np.ndarray, x_array: np.ndarray, y_array: np.ndarray, z_array: np.ndarray):
    # from the per_list, get the 3D perturbation array
    for ilon in prange(421):
        for ilat in range(MODEL_SHAPE[1]):
            for idep in range(MODEL_SHAPE[2]):
                for isrc in range(psf_list.shape[0]):
                    dist_sq = 0.5*((psf_list[isrc, 0]-x_array[ilon, ilat, idep])**2+(psf_list[isrc, 1]-y_array[ilon, ilat, idep])**2+(
                        psf_list[isrc, 2]-z_array[ilon, ilat, idep])**2)/(psf_list[isrc, 3]/6371.)**2
                    if dist_sq < 10.:
                        per_array[ilon, ilat, idep] = per_array[ilon,
                                                                ilat, idep]+psf_list[isrc, 4]*np.exp(-dist_sq)


def get_perturbation_array(psf_input: str, psf_output: str) -> np.ndarray:
    """get psf perturbation input model

    Args:
        psf_input (str): psf_list input txt path
        psf_output (str): the output xarray from .nc file

    Returns:
        np.ndarray: output 3D model
    """
    cache_name = "psf_cache"
    loaded = load_cache(cache_name)
    if loaded is not None:
        return loaded
    # * no cache
    # eara2022/resource/psf/psf_list.txt
    psf_list = np.loadtxt(psf_input)
    data = xr.open_dataset(psf_output)

    # get the 3d array
    per_array = np.zeros(MODEL_SHAPE, dtype=np.float)
    lat_array = np.zeros(MODEL_SHAPE, dtype=np.float)
    for index in range(MODEL_SHAPE[1]):
        lat_array[:, index, :] = data.latitude.data[index]
    lon_array = np.zeros(MODEL_SHAPE, dtype=np.float)
    for index in range(MODEL_SHAPE[0]):
        lon_array[index, :, :] = data.longitude.data[index]
    dep_array = np.zeros(MODEL_SHAPE, dtype=np.float)
    for index in range(MODEL_SHAPE[2]):
        dep_array[:, :, index] = data.depth.data[index]
    x_array = np.zeros(MODEL_SHAPE, dtype=np.float)
    y_array = np.zeros(MODEL_SHAPE, dtype=np.float)
    z_array = np.zeros(MODEL_SHAPE, dtype=np.float)

    # convert
    latlondep2xyz_sphere(lat_array, lon_array, dep_array,
                         x_array, y_array, z_array)
    get_per(per_array, psf_list, x_array, y_array, z_array)

    # save cache
    save_cache(file_name=cache_name, content=per_array)

    return per_array
