""" 
project_ehb.py

Project the EHB catalog to the given line using pygmt.project.
"""

from typing import Tuple

import pandas as pd
from pygmt import project

from eara2022 import resource
from obspy.geodetics.base import degrees2kilometers


def project_ehb_catalog(start:Tuple[float,float],end:Tuple[float,float],width:float=100,degree_limit=25)->pd.DataFrame:
    ehb_catalog=resource(['isc_ehb','isc_ehb.csv'],normal_path=True)
    df=pd.read_csv(ehb_catalog)
    # change column names from lat,lon,dep to y,x,z
    df.columns=['y','x','z',"id"]
    df=df.reindex(columns=['x','y','z',"id"])

    # project the catalog to the line
    res=project(
        data=df,
        center=list(start),
        endpoint=list(end),
        convention="pz",
        unit=True,
        sort=True,
        length=[0,degrees2kilometers(degree_limit)],
        width=[0,width],
    )

    # change column names back to lat,lon,dep
    res.columns=['dist','dep','id']
    # convert dist from km to degree
    res['dist']=res['dist'].apply(lambda x: x/degrees2kilometers(1))
    return res