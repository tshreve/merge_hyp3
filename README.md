# hyp3_merge
This package is for merging Sentinel-1 interferograms from Alaska Satellite Facility's Hybrid Pluggable Processing Pipeline (HyP3). Interferograms can be ordered frame-by-frame using HyP3, and this tool allows for merging the various geotiff products over a larger area for a given path. Output merged geotiffs can be input directly into Mintpy for time-series analysis. The minimum requried products downloaded from HyP3 are ```*_unw_phase.tif```, ```*_dem.tif```,  ```*_corr.tif```, ```*_lv_theta.tif```, ```*_lv_phi.tif```, and ```*_water_mask.tif```.
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

2. Install dependencies using *hyp3_merge_dependencies.txt* in a conda environment:
```bash
echo 'affine
dask
gdal
hyp3_sdk
rasterio
matplotlib' > hyp3_merge_dependencies.txt
 ```

```bash
conda create --name hyp3_proc --file hyp3_merge_dependencies.txt
 ```

## Usage
To run the project, use the following command:
```bash
./hyp3_par.py abs_path rel_data_folder rel_merge_folder num2merge [dst_crs] [coh_thresh]
```

where: <br>
```abs_path``` : absolute path to your data and merged folders <br>
```rel_data_folder``` : relative path to your data folder  <br>
```rel_merge_folder```: relative path to your merged data folder  <br>
```num2merge``` : number of frames to merge in the given path  <br>
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

