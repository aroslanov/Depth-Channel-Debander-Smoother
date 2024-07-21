# Depth Image Smoother

This Python script is designed to reduce banding artifacts in depth images while preserving important details. It converts 16-bit PNG depth images to 32-bit floating-point EXR format, applying advanced smoothing techniques in the process.

## Features

- Reads 16-bit PNG depth images
- Applies a two-scale bilateral filtering approach to reduce banding
- Enhances fine details using a detail boosting step
- Performs edge-aware smoothing as a final pass
- Saves the result as a 32-bit floating-point EXR file
- Provides user-controllable parameters for fine-tuning the smoothing process

## Requirements

- Python 3.6+
- NumPy
- OpenCV (cv2)
- OpenEXR

You can install the required libraries using pip:

```
pip install numpy opencv-python OpenEXR
```

Note: OpenEXR might require additional system libraries to be installed, depending on your operating system.

## Usage

```
python depth_smoother.py [--i INPUT_FILE] [--o OUTPUT_FILE] [options]
```

### Command-line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--i`, `--input_file` | "input.png" | Input depth image file (PNG format) |
| `--o`, `--output_file` | "output.exr" | Output EXR file |
| `--large_scale` | 15 | Large scale bilateral filter size |
| `--fine_scale` | 3 | Fine scale bilateral filter size |
| `--boost` | 1.5 | Detail boost factor |
| `--detail_threshold` | 0.02 | Detail preservation threshold |
| `--spatial_sigma` | 50.0 | Spatial sigma for edge-preserving smoothing |
| `--range_sigma` | 0.1 | Range sigma for edge-preserving smoothing |

### Detailed Explanation of Parameters

- `large_scale`: Controls the size of the large-scale bilateral filter. Higher values smooth larger areas but may reduce detail.
- `fine_scale`: Controls the size of the fine-scale bilateral filter. Lower values preserve more fine details.
- `boost`: Factor to enhance fine details. Values greater than 1.0 increase detail contrast.
- `detail_threshold`: Threshold for preserving details. Lower values preserve more subtle details.
- `spatial_sigma`: Controls the spatial extent of the edge-preserving smoothing. Higher values blur over larger spatial regions.
- `range_sigma`: Controls the range (intensity) sensitivity of the edge-preserving smoothing. Lower values preserve more edges.

## Examples

1. Basic usage with default parameters:
   ```
   python depth_smoother.py --i your_depth_image.png --o smoothed_depth.exr
   ```

2. Custom smoothing parameters:
   ```
   python depth_smoother.py --i your_depth_image.png --o smoothed_depth.exr --large_scale 20 --fine_scale 5 --boost 2.0 --detail_threshold 0.03 --spatial_sigma 60.0 --range_sigma 0.15
   ```

## Tips for Best Results

- Start with the default parameters and adjust them based on your specific depth images.
- If the output shows too much smoothing, try decreasing `large_scale` or increasing `detail_threshold`.
- To enhance fine details, increase the `boost` parameter, but be cautious of amplifying noise.
- Adjust `spatial_sigma` and `range_sigma` to fine-tune the edge-preserving smoothing effect.

## Contributing

Contributions to improve the script are welcome. Please feel free to submit issues or pull requests on the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.