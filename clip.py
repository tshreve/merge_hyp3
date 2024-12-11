#!/usr/bin/env python

from __future__ import division

from pathlib import Path
from typing import List, Union
from osgeo import gdal
import os

import affine
from pathlib import Path

import rasterio as rs
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio import shutil as rio_shutil
from rasterio.vrt import WarpedVRT
import dask
from dask.distributed import Client

def get_common_overlap(file_list: List[Union[str, Path]]) -> List[float]:
    """Get the common overlap of  a list of GeoTIFF files

    Arg:
        file_list: a list of GeoTIFF files

    Returns:
         [ulx, uly, lrx, lry], the upper-left x, upper-left y, lower-right x, and lower-right y
         corner coordinates of the common overlap
    """
    corners = []
    file_list_new = []
    for dem in file_list:
      corner_dem = rs.Info(str(dem), format='json')['cornerCoordinates']
      corners.append(corner_dem)
      #print(f"File {dem} has coordinates {corner_dem}")

    ulx = max(corner['upperLeft'][0] for corner in corners)
    uly = min(corner['upperLeft'][1] for corner in corners)
    lrx = min(corner['lowerRight'][0] for corner in corners)
    lry = max(corner['lowerRight'][1] for corner in corners)
    return [ulx, uly, lrx, lry]

def clip_files(file,vrt_options):

    #https://rasterio.readthedocs.io/en/latest/topics/virtual-warping.html

    print(file)
    outfile = file.parent / f'{file.stem}_resamp{file.suffix}'
    if os.path.isfile(outfile):
        print(outfile, " exists, skipping")
    else:
        with rs.open(file) as src:

            with WarpedVRT(src, **vrt_options) as vrt:

                # At this point 'vrt' is a full dataset with dimensions,
                # CRS, and spatial extent matching 'vrt_options'.

                # Read all data into memory.
                #data = vrt.read()

                # Process the dataset in chunks.  Likely not very efficient.
                #for _, window in vrt.block_windows():
                #    data = vrt.read(window=window)

                # Dump the aligned data into a new file.  A VRT representing
                # this transformation can also be produced by switching
                # to the VRT driver.
                outfile = file.parent / f'{file.stem}_resamp{file.suffix}'
                rio_shutil.copy(vrt, outfile, driver='GTiff')
    #gdal.Translate(destName=str(file.parent / f'{file.stem}_clipped{file.suffix}'), srcDS=str(file), projWin=overlap)
    return


def clip(mege_folder):

    data_dir = Path(mege_folder)

    files = data_dir.glob('*/*_dem.tif')
    overlap = get_common_overlap(files)
    print("Overlap is", overlap)

    dst_crs = 'EPSG:4326'

    # These coordinates are in UTM
    dst_bounds = overlap[0], overlap[3], overlap[2], overlap[1]

    # Output image dimensions
    dst_height = 6036
    dst_width = 4847

    # Output image transform
    left, bottom, right, top = dst_bounds
    xres = (right - left) / dst_width
    yres = (top - bottom) / dst_height
    dst_transform = affine.Affine(xres, 0.0, left,
                                0.0, -yres, top)

    vrt_options = {
        'resampling': Resampling.cubic,
        'crs': dst_crs,
        'transform': dst_transform,
        'height': dst_height,
        'width': dst_width,
    }

    results = []
    extensions = ['_unw_phase.tif'] #['_dem.tif','_corr.tif','_water_mask.tif','_lv_theta.tif', '_lv_phi.tif','_unw_phase.tif']


    for extension in extensions:
        for file in data_dir.rglob(f'*{extension}'):
            print(file)
            result = dask.delayed(clip_files)(file,vrt_options)
            results.append(result)

    futures = dask.persist(*results)
    results = dask.compute(*futures)

if __name__ == '__main__':
    import sys

    client = Client(threads_per_worker=2, n_workers=5)
    print(client.dashboard_link)

    if len(sys.argv) < 2:
        print("Usage: clip.py merge_folder")
        sys.exit(1)
    elif len(sys.argv) == 2:
        clip(sys.argv[1])