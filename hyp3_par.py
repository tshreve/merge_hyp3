#!/usr/bin/env python

def hyp3_par(path,data_folder,merge_folder,num2merge,dst_crs = 'EPSG:4326',coh_thresh = 0.95):
    import os
    import dask
    from dask.distributed import Client
    from run_merge import setup,run_merge
    ################################################
    
    if __name__ == '__main__':
        client = Client(threads_per_worker=2, n_workers=1)
        print(client.dashboard_link)


    hyp3_results = []

    #path = ''

    root_dir, intf_dates_dict = setup(path,data_folder)

    #coh_thresh = 0.95
    #num2merge = 3 
    #merge_folder = 'merged'
    #dst_crs = 'EPSG:4326'

    suffixes = ['corr.tif','dem.tif', 'lv_theta.tif', 'lv_phi.tif', 'water_mask.tif']#,'unw_phase.tif',
    outfiles_ll = []

    for _, value in intf_dates_dict.items():
            
        # number of interferograms for a single date pair
        num_vals = len([item for item in value if item])

        # merge the date pair if there are enough interferograms
        if num_vals >= num2merge:

            new_fold = root_dir / merge_folder / os.path.basename(value[0])
            os.makedirs(new_fold,exist_ok=True)
            merged_datasets = []
            final_outputs_path = []

            for suff in suffixes:
                hyp3_result = dask.delayed(run_merge)(value,num_vals,new_fold,suff,outfiles_ll,merge_folder,root_dir,merged_datasets,final_outputs_path,coh_thresh,dst_crs)
                hyp3_results.append(hyp3_result)

            futures = dask.persist(*hyp3_results) 
            results = dask.compute(*futures)

    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: hyp3_par.py abs_path rel_data_folder rel_merge_folder num2merge [dst_crs] [coh_thresh]")
        sys.exit(1)
    elif len(sys.argv) == 5:
        hyp3_par(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]))
    elif len(sys.argv) == 6:
        hyp3_par(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),sys.argv[5])
    elif len(sys.argv) == 7:
        hyp3_par(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),sys.argv[5],float(sys.argv[6]))