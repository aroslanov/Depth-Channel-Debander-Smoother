import numpy as np
import cv2
import OpenEXR
import Imath
import argparse
import sys

def read_image(file_path):
    img = cv2.imread(file_path, cv2.IMREAD_ANYDEPTH)
    if img is None:
        raise ValueError(f"Could not read image: {file_path}")
    return img.astype(np.float32)

def normalize_image(image):
    return (image - np.min(image)) / (np.max(image) - np.min(image))

def reduce_banding(image, large_scale=15, fine_scale=3, boost=1.5, detail_threshold=0.02):
    # Large scale bilateral filter
    large_smooth = cv2.bilateralFilter(image, d=large_scale, sigmaColor=0.1, sigmaSpace=large_scale)
    
    # Fine scale bilateral filter
    fine_smooth = cv2.bilateralFilter(image, d=fine_scale, sigmaColor=0.1, sigmaSpace=fine_scale)
    
    # Calculate detail layer
    detail = image - fine_smooth
    
    # Boost fine details
    boosted = fine_smooth + detail * boost
    
    # Combine large scale smooth with boosted fine details
    result = np.where(np.abs(detail) > detail_threshold, boosted, large_smooth)
    
    return normalize_image(result)

def edge_preserving_smooth(image, spatial_sigma, range_sigma):
    return cv2.bilateralFilter(image, d=-1, sigmaColor=range_sigma, sigmaSpace=spatial_sigma)

def save_exr(file_path, image):
    image_float32 = image.astype(np.float32)
    image_flat = image_float32.tobytes()

    header = OpenEXR.Header(image.shape[1], image.shape[0])
    header['channels'] = dict(Y=Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)))

    exr = OpenEXR.OutputFile(file_path, header)
    exr.writePixels({'Y': image_flat})
    exr.close()

def process_depth_image(input_path, output_path, large_scale, fine_scale, boost, detail_threshold, spatial_sigma, range_sigma):
    try:
        depth_map = read_image(input_path)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    normalized = normalize_image(depth_map)
    
    # First pass: reduce banding
    smoothed = reduce_banding(normalized, large_scale, fine_scale, boost, detail_threshold)
    
    # Second pass: edge-preserving smoothing
    final = edge_preserving_smooth(smoothed, spatial_sigma, range_sigma)
    
    try:
        save_exr(output_path, final)
    except Exception as e:
        print(f"Error saving EXR file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Depth Image Banding Reduction")
    parser.add_argument("--i", "--input_file", dest="input_file", help="Input depth image file (PNG)", default="input.png")
    parser.add_argument("--o", "--output_file", dest="output_file", help="Output EXR file", default="output.exr")
    parser.add_argument("--large_scale", type=int, default=15, help="Large scale bilateral filter size")
    parser.add_argument("--fine_scale", type=int, default=3, help="Fine scale bilateral filter size")
    parser.add_argument("--boost", type=float, default=1.5, help="Detail boost factor")
    parser.add_argument("--detail_threshold", type=float, default=0.02, help="Detail preservation threshold")
    parser.add_argument("--spatial_sigma", type=float, default=50.0, help="Spatial sigma for edge-preserving smoothing")
    parser.add_argument("--range_sigma", type=float, default=0.1, help="Range sigma for edge-preserving smoothing")
    
    args = parser.parse_args()
    
    print(f"Processing depth image: {args.input_file}")
    print(f"Output will be saved as: {args.output_file}")
    
    process_depth_image(args.input_file, args.output_file, 
                        args.large_scale, args.fine_scale, args.boost, args.detail_threshold,
                        args.spatial_sigma, args.range_sigma)
    
    print(f"Processed depth image saved as {args.output_file}")

if __name__ == "__main__":
    main()