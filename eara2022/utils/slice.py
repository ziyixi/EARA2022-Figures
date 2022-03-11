""" 
slice.py

helper functions in cuting cross-sections, make projections.
"""
from typing import List, Tuple

import numpy as np
import pyproj
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import KDTree


def model_interp(to_interp_data: xr.DataArray, lons: np.ndarray, lats: np.ndarray, deps: np.ndarray) -> np.ndarray:
    """Give an xarray model, interp it based on the given lats, lons, deps and construct a new xarray dataset.
    mainly used to generate the vertical cross-sections

    Args:
        to_interp_data (xr.DataArray): the data array to interp
        lons (np.ndarray): the longitude array
        lats (np.ndarray): the latitude array, define a line with lons on the plane
        deps (np.ndarray): the depth array

    Returns:
        np.ndarray: the interp result
    """
    # * len(lons) should be the same as len(lats)
    profile_list = []
    for idep in range(len(deps)):
        for ilon in range(len(lons)):
            profile_list.append([lons[ilon], lats[ilon], deps[idep]])
    model_interpolating_function = RegularGridInterpolator(
        (to_interp_data.longitude.data, to_interp_data.latitude.data, to_interp_data.depth.data), to_interp_data.data)
    interp_result: np.ndarray = model_interpolating_function(profile_list)
    cross_section = np.zeros((len(lons), len(deps)))

    icount = 0
    for idep in range(len(deps)):
        for ilon in range(len(lons)):
            cross_section[ilon, idep] = interp_result[icount]
            icount += 1

    return cross_section


def topo_interp(to_interp_data: xr.DataArray, lons: np.ndarray, lats: np.ndarray) -> np.ndarray:
    """Give the xarray topography model, interp the elevation line along the given (lons,lats) pair. 

    Args:
        to_interp_data (xr.DataArray): the input topo data array
        lons (np.ndarray): the longitude array
        lats (np.ndarray): the latitude array, define a line with lons on the plane

    Returns:
        np.ndarray: the interp topo result
    """
    profile_list = []
    for ilon in range(len(lons)):
        profile_list.append([lons[ilon], lats[ilon]])
    # the names and the transverse might be adjusted, this is the gmt format
    grd_interpolating_function = RegularGridInterpolator(
        (to_interp_data.lon.data, to_interp_data.lat.data), to_interp_data.data.T)

    grd_interp_result = grd_interpolating_function(profile_list)

    # * return the 1d array
    return grd_interp_result


def gmt_lat_as_dist(start: Tuple[float, float], end: Tuple[float, float], a_list: List[float], g_interval: List[float], npts: int = 1001) -> str:
    pass
