#!/usr/bin/env python

# To do : Process multiple files at once - perform operations on groups of files simultaneously
# Look at : https://examples.dask.org/applications/embarrassingly-parallel.html


from statistics import mean
import multiprocessing
from pathlib import Path
import os
import glob
import rasterio as rs
import dask


from hyp3_merge import utils_merge as ut
from hyp3_merge import search


def setup(path,data_folder):
    # set path to data directories
    ##path = 
    root_dir = Path(path)

    intf_dates_dict = search.search_intf(root_dir,data_folder)

    # set coherence threshold
    ##coh_thresh = 0.95

    # define minimum number of interferograms to merge
    ##num2merge = 3

    ##merge_folder = 'merged'

    ##dst_crs = 'EPSG:4326'

    # define suffixes of files to merge


    return root_dir, intf_dates_dict

# loop through interferogram dates

def run_merge(value,num_vals,new_fold,suff,outfiles_ll,merge_folder,root_dir,merged_datasets,final_outputs_path,coh_thresh,dst_crs):


    # copy necessary text files and check if files already exist
    existing_files, final_outputs, = ut.merge_setup(value,root_dir,suff,num_vals,new_fold,merge_folder)

    datasets = []
    files = []
    

    if existing_files:
        print(f"Files {existing_files} already exists. Skipping processing.")
    else:
        # open each interferogram or datafile
        for image in value:
            for file in image.glob(f'*{suff}'):
                files.append(file)
                dataset = rs.open(file)
                outfile_ll, inp_crs = ut.utm2latlon(dataset,file,dst_crs)
                outfiles_ll.append(outfile_ll)
                dataset_n = rs.open(outfile_ll)
                datasets.append(dataset_n)

        # if interferogram, reference values in overlap regions accordingly
        if suff == 'unw_phase.tif':
            #try:
            merged_dataset, final_output = ut.merge_intfs(files, value, datasets, new_fold, suff, coh_thresh)
            #except Exception as e:
            #  print(f"{e}; continuing")
            #  continue

        # merge all other datasets that do not require referencing (coherence, dem, water mask, etc.)
        #! Except to avoid issues when different CRS. Convert to lat/lon to avoid issues: https://gis.stackexchange.com/questions/311837/mosaicking-images-with-different-crs-using-rasterio
        else:
            #try:
            merged_dataset, final_output = ut.merge_datasets(datasets, new_fold, value, suff)
            #except Exception as e:
            #  print(f"{e}; continuing")
            #  continue
        ##merged_datasets.append(merged_dataset)
        ##final_outputs_path.append(final_output)
    ##print("Final output paths are", final_outputs_path)
    ##for i, merged in enumerate(merged_datasets):
    ##    outfile = ut.latlon2utm(merged,final_outputs_path[i],inp_crs)
    ##    os.rename(outfile,final_outputs_path[i])

    return
#def printVal(value):
#    return ("hello "*(value))
#pool_obj = multiprocessing.Pool()
#ans = pool_obj.map(printVal,range(0,4))
#print(ans)
#pool_obj.close()
