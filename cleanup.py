#!/usr/bin/env python

import os
import sys

def remove_files_with_suffix_test(directory, suffix):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(suffix):
                file_path = os.path.join(directory, filename)
                print(f"Will remove file: {file_path}")

def remove_files_with_suffix_final(directory, suffix):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(suffix):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                print(f"Will remove file: {file_path}")



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: cleanup.py abs_merge_path abs_data_path")
        sys.exit(1)
    merge_directory = sys.argv[1]
    data_directory = sys.argv[2]
    remove_files_with_suffix_test(data_directory, '_ll.tif')
    remove_files_with_suffix_test(merge_directory, '_unw_phase_shifted.tif')
    remove_files_with_suffix_test(merge_directory, '_corr.tif')
    remove_files_with_suffix_test(merge_directory, '_dem.tif')
    remove_files_with_suffix_test(merge_directory, '_lv_phi.tif')
    remove_files_with_suffix_test(merge_directory, '_lv_theta.tif')
    remove_files_with_suffix_test(merge_directory, '_merged_water.tif')
    remove_files_with_suffix_test(merge_directory, '_unw_phase.tif')

    confirm = input(f"Are you sure you want to remove files with specified suffixes in {merge_directory} and {data_directory}? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        sys.exit(0)
    elif confirm.lower() == 'yes':
        remove_files_with_suffix_final(data_directory, '_ll.tif')
        remove_files_with_suffix_final(merge_directory, '_unw_phase_shifted.tif')
        remove_files_with_suffix_final(merge_directory, '_corr.tif')
        remove_files_with_suffix_final(merge_directory, '_dem.tif')
        remove_files_with_suffix_final(merge_directory, '_lv_phi.tif')
        remove_files_with_suffix_final(merge_directory, '_lv_theta.tif')
        remove_files_with_suffix_final(merge_directory, '_merged_water.tif')
        remove_files_with_suffix_final(merge_directory, '_unw_phase.tif')