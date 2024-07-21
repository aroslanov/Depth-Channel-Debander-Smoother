# Depth Image Banding Reduction with HDR Extension

This project provides a script to process depth images by reducing banding and extending the dynamic range. The processed images are saved in the EXR format. The script supports various input image formats, including PNG, JPG, TIFF, and EXR.

## Features
- Reads and processes depth images.
- Reduces banding artifacts using bilateral filters.
- Extends the dynamic range of depth images.
- Saves the processed images in EXR format.

## Requirements
- Python 3.x
- NumPy
- OpenCV
- OpenEXR
- Imath
- Pillow

## Installation
Install the required Python packages using pip:
```bash
pip install numpy opencv-python-headless OpenEXR Imath pillow
```

## Usage
Run the script from the command line with the necessary arguments:
```bash
python process_depth_image.py --i input.png --o output.exr --large_scale 15 --fine_scale 3 --boost 1.5 --detail_threshold 0.02 --spatial_sigma 50.0 --range_sigma 0.1 --black_point 0.0 --white_point 1.0
```

### Command Line Parameters

- `--i`, `--input_file` (default: "input.png")
  - The input depth image file. Supported formats include PNG, JPG, TIFF, and EXR.
  
- `--o`, `--output_file` (default: "output.exr")
  - The output EXR file where the processed image will be saved.
  
- `--large_scale` (default: 15)
  - The filter size for the large-scale bilateral filter, which is used to smooth the image and reduce banding.
  
- `--fine_scale` (default: 3)
  - The filter size for the fine-scale bilateral filter, which is used for detailed smoothing.
  
- `--boost` (default: 1.5)
  - The detail boost factor. Higher values will enhance the details in the image.
  
- `--detail_threshold` (default: 0.02)
  - The threshold for detail preservation. Details above this threshold will be preserved during smoothing.
  
- `--spatial_sigma` (default: 50.0)
  - The spatial sigma for edge-preserving smoothing. Controls the extent of smoothing in the spatial domain.
  
- `--range_sigma` (default: 0.1)
  - The range sigma for edge-preserving smoothing. Controls the extent of smoothing in the intensity domain.
  
- `--black_point` (default: None)
  - The black point for dynamic range extension. Must be between 0.0 and 1.0. If specified, `white_point` must also be specified.
  
- `--white_point` (default: None)
  - The white point for dynamic range extension. Must be between 0.0 and 1.0 and greater than `black_point`. If specified, `black_point` must also be specified.

## Example
To process a depth image named `depth.png` and save the result as `processed.exr` with specific parameters:
```bash
python process_depth_image.py --i depth.png --o processed.exr --large_scale 20 --fine_scale 5 --boost 2.0 --detail_threshold 0.01 --spatial_sigma 60.0 --range_sigma 0.2 --black_point 0.05 --white_point 0.95
```

## Script Explanation

### `read_image(file_path)`
Reads an image file. If the file is an EXR file, it calls `read_exr(file_path)`; otherwise, it uses OpenCV or Pillow to read the image. Converts the image to grayscale and normalizes it to the range [0.0, 1.0].

### `read_exr(file_path)`
Reads an EXR file and returns the image data as a NumPy array.

### `normalize_image(image)`
Normalizes the image data to the range [0.0, 1.0].

### `extend_dynamic_range(image, black_point, white_point)`
Extends the dynamic range of the image by clipping values below the black point and above the white point, then normalizing the image based on the new black and white points.

### `process_depth_image(input_path, output_path, large_scale, fine_scale, boost, detail_threshold, spatial_sigma, range_sigma, black_point, white_point)`
Processes the depth image by reading it, extending its dynamic range, reducing banding, and applying edge-preserving smoothing. Saves the processed image as an EXR file.

### `reduce_banding(image, large_scale, fine_scale, boost, detail_threshold)`
Reduces banding in the image using bilateral filters at large and fine scales, boosts details, and normalizes the result.

### `edge_preserving_smooth(image, spatial_sigma, range_sigma)`
Applies edge-preserving smoothing to the image using a bilateral filter.

### `save_exr(file_path, image)`
Saves the image as an EXR file.

### `main()`
Parses command line arguments and calls `process_depth_image()` with the provided parameters.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.