#!/usr/bin/env python

import rasterio as rs
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.plot import show
from rasterio.merge import merge
from rasterio.transform import rowcol

import re
from osgeo import gdal
import numpy as np
import shutil
import matplotlib.pyplot as plt
import glob
import os 

def reference_dataset(dataset, outpath, lat, lon):
  '''
  Reference a SAR frame to a given point.

  Parameters: dataset - Open rasterio dataset
              outpath - Path to save shifted dataset
              lat - Reference point latitude
              lon - Reference point longitude
  Returns:    shifted_dataf - Open shifted rasterio dataset
              px - Pixel x-coordinate of reference point
              py - Pixel y-coordinate of reference point
  '''
##############################################################

  # Convert geographic coordinates to pixel coordinates
  py, px = rowcol(dataset.transform, lon, lat)

  # Read the value at the pixel coordinates
  value_at_point = dataset.read(1)[int(py), int(px)]
  print(f"Value at ({lon}, {lat}): {value_at_point}")

  # Read the entire dataset into a numpy array
  data = dataset.read(1)

  # Set zeros to nan so not affected by shift
  data[data == 0] = 'nan'

  # Apply the shift to all values in the dataset, set nan back to zero
  shifted_data = data - value_at_point
  shifted_data[np.isnan(shifted_data)] = 0

  # Copy metadata and save file
  out_meta = dataset.meta.copy()
  out_meta.update({
  "driver": "GTiff",
  "height": shifted_data.shape[0],
  "width": shifted_data.shape[1],
  "transform": dataset.transform,
  "crs": dataset.crs
  })

  with rs.open(outpath, "w", **out_meta) as dest:
      dest.write(shifted_data, 1)
      print("Saved file ", outpath)

  # Open file for further processing
  shifted_dataf = rs.open(outpath)

  return value_at_point, shifted_dataf, px, py


def reference_dataset2(dataset1, dataset2, outpath, lat, lon):
  '''
  Shift SAR frame values so referenced to a nearby frame.

  Parameters: dataset1 - Open rasterio dataset to choose reference value
              dataset2 - Open rasterio dataset to shift
              outpath - Path to save shifted dataset
              lat - Reference point latitude
              lon - Reference point longitude
  Returns:    shifted_dataf - Open shifted rasterio dataset
              px - Pixel x-coordinate of reference point in shifted dataset
              py - Pixel y-coordinate of reference point in shifted dataset
  '''
##############################################################

  # Convert geographic coordinates to pixel coordinates
  py, px = rowcol(dataset1.transform, lon, lat)
  py1, px1 = rowcol(dataset2.transform, lon, lat)

  # Read the value at the pixel coordinates
  value_at_point = dataset1.read(1)[int(py), int(px)]
  value_at_point1 = dataset2.read(1)[int(py1), int(px1)]

  print(f"Value at ({lon}, {lat}) for dataset1: {value_at_point}")
  print(f"Value at ({lon}, {lat}) for dataset2: {value_at_point1}")

  # Calculate difference between two datasets at reference point
  final_value = value_at_point - value_at_point1
  print(f"Final shifted value is {final_value}")

  # Read the entire dataset into a numpy array
  data = dataset2.read(1)

  # Set zeros to nan so not affected by shift
  data[data == 0] = 'nan'

  # Apply the shift to all values in the dataset, set nan back to zero
  shifted_data = data + final_value
  shifted_data[np.isnan(shifted_data)] = 0

  # Copy metadata and save file
  out_meta = dataset2.meta.copy()
  out_meta.update({
  "driver": "GTiff",
  "height": shifted_data.shape[0],
  "width": shifted_data.shape[1],
  "transform": dataset2.transform,
  "crs": dataset2.crs
  })

  with rs.open(outpath, "w", **out_meta) as dest:
      dest.write(shifted_data, 1)
      print("Saved file ", outpath)

  # Open file for further processing
  shifted_dataf = rs.open(outpath)

  return shifted_dataf, px1, py1

def get_non_zero_lat_lon(dataset):
  '''
  Extract all latitudes and longitudes with non-zero raster values.

  Parameters: dataset - Open rasterio dataset
  Returns:    lat_lon_coords - N Latitudes and longitudes with non-zero raster values, in an array of shape (N,2)---!
  '''
##############################################################

  # Read the entire dataset into a numpy array
  data = dataset.read(1)

  # Identify the non-zero values
  non_zero_indices = np.nonzero(data)

  # Get the row and column indices of non-zero values
  rows, cols = non_zero_indices

  # Convert pixel coordinates to geographic coordinates in batch
  lon, lat = dataset.xy(rows, cols)

  # Combine lat and lon into a single array
  lat_lon_coords = np.column_stack((lat, lon))

  return lat_lon_coords

#! This could be sped up
def find_matching_rows(array1, array2):
  '''
  Find overlapping areas in two rasters.

  Parameters: array1 - Array of latitudes/longitudes for first rasterio dataset
              array2 - Array of latitudes/longitudes for second rasterio dataset
  Returns:    matching_rows - Latitudes/longitudes of overlapping areas.
  '''
##############################################################

  # Round lat/lon to chosen decimal place
  round = 3
  print(f"Rounding lat/lon to {round} decimal places.")
  # Convert the rows of the arrays to a structured array type
  arr1_round = np.round(array1, round)
  arr2_round = np.round(array2, round)

  dtype = np.dtype((np.void, arr1_round.dtype.itemsize * arr1_round.shape[1]))
  structured_array1 = np.ascontiguousarray(arr1_round).view(dtype)
  structured_array2 = np.ascontiguousarray(arr2_round).view(dtype)

  # Find the intersection of the structured arrays
  matching_structured_rows = np.intersect1d(structured_array1, structured_array2)

  # Convert the structured array back to the original shape
  matching_rows = matching_structured_rows.view(arr1_round.dtype).reshape(-1, arr1_round.shape[1])

  return matching_rows


def sort_arrays_by_min_value(arrays):
    """
    Sort a list of arrays based on the minimum value in each array.

    Parameters: List of numpy arrays.
    Returns: Sorted list of numpy arrays.
    """
    # Define a key function that returns the minimum value in the array
    def min_value_lat(array):
        return np.min(array[:,1])

    # Enumerate the arrays to keep track of their original indexes
    indexed_arrays = list(enumerate(arrays))

    # Sort the list of arrays using the key function
    sorted_indexed_arrays = sorted(indexed_arrays, key=lambda x: min_value_lat(x[1]))

    sorted_arrays = [array for index, array in sorted_indexed_arrays]
    sorted_indexes = [index for index, array in sorted_indexed_arrays]

    return sorted_arrays, sorted_indexes



def extract_dates(folder_name):
    """
    Extract YYYYMMDD date strings from the given folder name using regular expressions.

    :param folder_name: The folder name containing the dates.
    :return: A tuple containing the extracted date strings.
    """
    # Define the regular expression pattern to match YYYYMMDD date strings
    pattern = r'(\d{8})T\d{6}_(\d{8})T\d{6}'

    # Search for the pattern in the folder name
    match = re.search(pattern, folder_name)

    if match:
        # Extract the dates from the match object
        date1 = match.group(1)
        date2 = match.group(2)
        return date1, date2
    else:
        return None


def check_files_exist(file_list):
    """
    Check if any elements of a list include filenames that exist in the given directory.

    Parameters:
    file_list (list): List of filenames to check.
    directory (str): Directory to check for the existence of files.

    Returns:
    bool: True if any files exist, False otherwise.
    """
    existing_files = []
    for filename in file_list:
        if os.path.exists(filename):
          existing_files.append(filename)

    return existing_files

def merge_datasets(datasets, new_fold, value, suff):
    """

    Merge a list of raster files into a single GeoTIFF file.

    Parameters:
    datasets (list) : list of images opened with rasterio
    value (list) : list with path to image folders
    suff (str) : suffix of image to merge

    Returns:
    merged_dataset (rasterio dataset) : opened merged image
    final_output (str) : path to merged image
    """

    #! method may need to be changed depending on the dataset
    mosaic, out_trans = merge(datasets, method = 'first')

    out_meta = datasets[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "crs": datasets[0].crs
    })

    # Save the merged dataset to a new GeoTIFF file
    path2 = '_merged_'+ suff
    final_output = new_fold / (os.path.basename(value[0]) + path2)
    with rs.open(final_output, "w", **out_meta) as dest:
        dest.write(mosaic)

    # Display the merged dataset
    merged_dataset = rs.open(final_output)
    #show(merged_dataset, title='Merged GeoTIFF')
    #plt.show()

    return merged_dataset, final_output

def merge_intfs(files, value, datasets, new_fold, suff, coh_thresh = 0.95):

    """

    Reference and merge a list of raster interferograms into a single GeoTIFF file. Reference points are in overlap regions of the interferograms, with coherence above a defined threshold.

    Parameters:
    files (list) : image paths
    value (list) : list with path to image folders
    datasets (list) : list of images opened with rasterio
    new_fold (str) : path to save merged images
    coh_thresh (float) : coherence threshold for reference point

    Returns:
    merged_dataset (rasterio dataset) : opened merged image
    final_output (str) : path to merged image

    """
    # open coherence file to determine referencing region
    path_c = '_merged_corr.tif'
    final_output_c = new_fold / (os.path.basename(value[0]) + path_c)
    print(final_output_c)
    try:
      coh_all = rs.open(final_output_c)
      coh_all_dat = coh_all.read(1)
    except:
      print("No merged coherence file.")

    lat_lons = []
    names = []
    outpaths = []

    # extract lats/lons that are nonzero
    for c,i in enumerate(datasets):
      lat_lon_coords = get_non_zero_lat_lon(i)
      lat_lons.append(lat_lon_coords)
    # sort images by latitude
    sorted_lat_lons,sorted_indexes = sort_arrays_by_min_value(lat_lons)

    # sort file names and output paths by latitude
    for d,j in enumerate(sorted_lat_lons):
      name, _ = os.path.splitext(os.path.basename(files[sorted_indexes[d]]))
      names.append(name)
      outpath = new_fold /  (name + '_shifted.tif')
      outpaths.append(outpath)
    print(outpaths)

    for k in range(len(sorted_lat_lons)-1):
      # reference first two interferograms based on same point
      if k==0:
        # choose pixel in overlap of both interferograms and extract coherence values
        coords = find_matching_rows(sorted_lat_lons[0], sorted_lat_lons[1])
        pyc1, pxc1 = rowcol(coh_all.transform, coords[0,1], coords[0,0])
        coh_h = coh_all_dat[int(pyc1),int(pxc1)]
        print(f"Coherence is {coh_h} at {coords[0,1]}, {coords[0,0]}")
        c = 0
        lat = coords[c][0]
        lon = coords[c][1]
        # if coherence value is less than threshold, keep looking for better coherence value
        try:
          while coh_h < coh_thresh:
              c = c + 1
              lat = coords[c][0]
              lon = coords[c][1]
              #lat, lon = find_matching_rows(lat_lon_coords0, lat_lon_coords1)[c]
              pyc1, pxc1 = rowcol(coh_all.transform, lon, lat)
              coh_h = coh_all_dat[int(pyc1),int(pxc1)]
        # if the pixel is at the edge of the interferograms, continue to next interferograms
        except Exception:
          print("Issue with indexing")
          continue
        print(f"Coherence is {coh_h} at {lon}, {lat}")

        # reference first and second interferograms
        print("Referencing first images at", lat, lon)
        value_at_point0, shifted_data0, px0, py0 = reference_dataset(datasets[sorted_indexes[0]], outpaths[0], lat, lon)
        value_at_point1, shifted_data1, px1, py1 = reference_dataset(datasets[sorted_indexes[1]], outpaths[1], lat, lon)

        # check for errors (ex: reference point at masked water body, corrupted images, etc.)
        if value_at_point0 == 0 or value_at_point1 == 0:
          print("Shifted values are zero, rerunning.")
          c = c + 1
          lat = coords[c][0]
          lon = coords[c][1]
          pyc1, pxc1 = rowcol(coh_all.transform, lon, lat)
          coh_h = coh_all_dat[int(pyc1),int(pxc1)] 
          while coh_h < coh_thresh:
            c = c + 1
            lat = coords[c][0]
            lon = coords[c][1]
            pyc1, pxc1 = rowcol(coh_all.transform, lon, lat)
            coh_h = coh_all_dat[int(pyc1),int(pxc1)] 
          print(f"Try2: Coherence is {coh_h} at {lon}, {lat}")
          print("Referencing first images at", lat, lon)
          value_at_point0, shifted_data0, px0, py0 = reference_dataset(datasets[sorted_indexes[0]], outpaths[0], lat, lon)
          value_at_point1, shifted_data1, px1, py1 = reference_dataset(datasets[sorted_indexes[1]], outpaths[1], lat, lon)

        if value_at_point0 == value_at_point1:
          print("Shifted values are the same, check your images please.")
          exit()
 

        # create array of shifted datasets
        shifted_data = [shifted_data0, shifted_data1]

      # for all subsequent interferograms, reference to a pixel value in the previous interferogram
      else:
        # extract nonzero lat/lons
        lat_lon_coords1_new = get_non_zero_lat_lon(shifted_data[k])
        # find matching rows
        common = find_matching_rows(lat_lon_coords1_new, sorted_lat_lons[k+1])
        pyc1, pxc1 = rowcol(coh_all.transform, common[0,1], common[0,0])
        coh_h = coh_all_dat[int(pyc1),int(pxc1)]
        print(f"Coherence is {coh_h} at {common[0,1]}, {common[0,0]}")
        c = 0
        try:
        # if coherence value is less than threshold, keep looking for better coherence value
          while coh_h < coh_thresh:
              c = c + 1
              #!How to deal with edge cases
              pyc1, pxc1 = rowcol(coh_all.transform, common[c,1], common[c,0])
              coh_h = coh_all_dat[int(pyc1),int(pxc1)]
        except Exception:
          print("Issue with indexing")
          continue

        print(f"Coherence is {coh_h} at {common[c,1]}, {common[c,0]}")
        # shift interferogram
        final_lon, final_lat = common[c,1], common[c,0]
        shifted_data_n, px2, py2 = reference_dataset2(shifted_data[k], datasets[sorted_indexes[k+1]], outpaths[k+1], final_lat, final_lon)
        shifted_data.append(shifted_data_n)

    # merge referenced interferograms, with pixel values from only one interferogram chosen in the overlaps
    mosaic, out_trans = merge(shifted_data, method = 'first')

    # copy and save metadata for merged interferogram
    out_meta = shifted_data[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "crs": shifted_data[0].crs
    })

    # save the merged dataset to a new GeoTIFF file
    path2 = '_merged_'+ suff
    final_output = new_fold / (os.path.basename(value[0]) + path2)
    with rs.open(final_output, "w", **out_meta) as dest:
        dest.write(mosaic)


    # display the merged dataset
    merged_dataset = rs.open(final_output)
    #show(merged_dataset, title='Merged GeoTIFF')
    #plt.show()

    return merged_dataset, final_output


def merge_setup(value,root_dir,suff,num_vals,new_fold,merge_folder):

    """
    Copy needed text files and check if merged files already exist.

    Parameters:
    value (list) : list with path to image folders
    root_dir (str) : root directory
    suff (str) : suffix of image to merge
    num_vals (int) : number of images to merge
    new_fold (str) : path to save merged images
    merge_folder (str) : name of parent folder for merged images

    Returns:
    existing_files (list) : list of files that already exist
    final_outputs (list) : output paths for merged images

    """
    final_outputs = []

    txt_files = glob.glob(os.path.join(value[0], '*.txt'))

    # copy necessary .txt files to the destination directory, if they exist
    for txt_file in txt_files:
      new_txt_file = new_fold / os.path.basename(txt_file)
      if not os.path.exists(new_txt_file):
        shutil.copy(txt_file, new_fold)
        print(f"Copied {txt_file} to {new_fold}")

    # check if any of possible interferograms have already been merged, otherwise begin processing
    #! could use regex to do this instead
    path2 = '_merged_'+ suff
    for i in range(num_vals):
      new_fold_n = root_dir / merge_folder / os.path.basename(value[i])
      final_outputs.append(new_fold_n / (os.path.basename(value[i]) + path2))

    print(final_outputs)
    existing_files = check_files_exist(final_outputs)

    return existing_files, final_outputs

def utm2latlon(dataset,file,dst_crs):
    """
    Convert from utm to lat/lon in case utm zone is different for sub-images.

    Parameters:
    dataset (obj) : dataset object of image
    file (str) : image directory
    dst_crs (str) : destination crs

    Returns:
    outfile (str) : path to converted image
    inp_crs (str) : input crs of image

    """
    base = os.path.basename(file)
    outfile = os.path.dirname(file) +'/' + os.path.splitext(base)[0]  + '_ll.tif'

    inp_crs = dataset.crs

    transform, width, height = calculate_default_transform(
    inp_crs, dst_crs, dataset.width, dataset.height, *dataset.bounds)
    kwargs = dataset.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })
    with rs.open(outfile, 'w', **kwargs) as dst:
      for i in range(1, dataset.count + 1):
          reproject(
              source=rs.band(dataset, i),
              destination=rs.band(dst, i),
              src_transform=dataset.transform,
              src_crs=dataset.crs,
              dst_transform=transform,
              dst_crs=dst_crs,
              resampling=Resampling.nearest)

    return outfile, inp_crs

def latlon2utm(dataset,file,inp_crs):
    """
    Convert from utm to lat/lon in case utm zone is different for sub-images.

    Parameters:
    dataset (obj) : dataset object of image
    file (str) : image directory

    Returns:
    outfile (str) : path to converted image

    """
    base = os.path.basename(file)
    outfile = os.path.dirname(file) +'/' + os.path.splitext(base)[0]  + '_utm.tif'

    #utm = rs.CRS.from_proj4('+proj=utm +zone=11')

    transform, width, height = calculate_default_transform(
    dataset.crs, inp_crs, dataset.width, dataset.height, *dataset.bounds)
    kwargs = dataset.meta.copy()
    kwargs.update({
        'crs': inp_crs,
        'transform': transform,
        'width': width,
        'height': height
    })
    with rs.open(outfile, 'w', **kwargs) as dst:
        for i in range(1, dataset.count + 1):
            reproject(
                source=rs.band(dataset, i),
                destination=rs.band(dst, i),
                src_transform=dataset.transform,
                src_crs=dataset.crs,
                dst_transform=transform,
                dst_crs=inp_crs,
                resampling=Resampling.nearest)

    return outfile