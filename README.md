# hyp3_merge
This package is for merging Sentinel-1 interferograms from Alaska Satellite Facility's Hybrid Pluggable Processing Pipeline (HyP3). Interferograms can be ordered frame-by-frame using HyP3, and this tool allows for merging the various geotiff products with the same reference and secondary dates over a larger area for a given path. Output merged geotiffs can be input directly into Mintpy for time-series analysis. The minimum requried products downloaded from HyP3 are ```*_unw_phase.tif```, ```*_dem.tif```,  ```*_corr.tif```, ```*_lv_theta.tif```, ```*_lv_phi.tif```, and ```*_water_mask.tif```. <br>
<br>
**Note 1**: Input geotiffs are converted from UTM to lat/lon due to processing errors when a path passes through multiple UTM zones. However, one should be aware that this coordinate transformation may introduce resampling errors. 
<br>
<br>
**Note 2**: The asf_search tool stack() will not identify scenes that have different frame numbers as potential interferogram pairs. However, when interferogram scenes span a frame drift, there will be a spatial gap. One way to identify these gaps is by using the [ASF Data Search](https://search.asf.alaska.edu/) online tool. Missing interferograms can be aquired by manually choosing the scene IDs which overlap in the gap and submitting a job to Hyp3. This is tedious, so any alternative methods would be useful!

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

- ## Installation
1. Clone the repository:
```bash
git clone https://github.com/tshreve/hyp3_merge.git
```

2. Install dependencies using ```hyp3_merge_dependencies.txt``` in a conda environment:
```bash
echo 'affine
dask
hyp3_sdk
rasterio
matplotlib' > hyp3_merge_dependencies.txt
 ```

```bash
conda create --name hyp3_proc --file hyp3_merge_dependencies.txt
 ```
3. Prep PYTHONPATH

```bash
export PYTHONPATH='/path/to/package:$PYTHONPATH'
 ```

## Usage
Ensure all your data folders are in the same location and create a destinate folder to put the merged files. The script will automatically find all folders that have the same interferogram reference/seconday dates. 

<br>
To run the project, use the following command:

```bash
./hyp3_par.py abs_path rel_data_folder rel_merge_folder num2merge unwrap [dst_crs] [coh_thresh]
```

where: <br>
```abs_path``` : absolute path to your data and merged folders <br>
```rel_data_folder``` : relative path to your data folder  <br>
```rel_merge_folder```: relative path to your merged data folder  <br>
```num2merge``` : minimum number of frames to merge in the given path  <br>
```unwrap``` : whether you want to merged interferograms (*IMPORTANT*: First run with ```unwrap=False```, then ```unwrap=True``` so coherence files are merged first. This workflow can be improved.) <br>
```dst_crs``` : desired output coordinate system (optional)  <br>
```coh_thresh``` : coherence threshold for choosing reference points for interferogram merging (optional; default = 0.95) <br>

## Contributing
Contributions are encouraged! I will do my best to continue updating this script, but if you've found ways to improve it on your own, feel free to create a PR using the following:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes.
4. Push your branch: `git push origin feature-name`.
5. Create a pull request.

Ideas for increased functionality are also welcome. Thanks to all who are helping to make InSAR more accessible!

## License
This project was funded by the Utah Geological Survey, and I am still figuring out licensing.

