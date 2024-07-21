import numpy as np
import cv2
import OpenEXR
import Imath
import argparse
import sys
from PIL import Image

def read_image(file_path):
    # Check if the file is an EXR
    if file_path.lower().endswith('.exr'):
        return read_exr(file_path)
    
    # For non-EXR files, use the existing method
    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        try:
            with Image.open(file_path) as pil_img:
                img = np.array(pil_img)
        except:
            raise ValueError(f"Could not read image: {file_path}")
    
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    if img.dtype == np.uint8:
        img = img.astype(np.float32) / 255.0
    elif img.dtype == np.uint16:
        img = img.astype(np.float32) / 65535.0
    else:
        img = img.astype(np.float32)
    
    return img

def read_exr(file_path):
    file = OpenEXR.InputFile(file_path)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    channelData = file.channel('Y', Imath.PixelType(Imath.PixelType.FLOAT))
    img = np.frombuffer(channelData, dtype=np.float32)
    img.shape = (size[1], size[0])
    return img

def normalize_image(image):
    return (image - np.min(image)) / (np.max(image) - np.min(image))

def extend_dynamic_range(image, black_point, white_point):
    # Convert black_point and white_point to float
    black_point = float(black_point)
    white_point = float(white_point)
    
    # Ensure white_point is greater than black_point
    if white_point <= black_point:
        raise ValueError("White point must be greater than black point")
    
    # Clip values below black point and above white point
    image = np.clip(image, black_point, white_point)
    
    # Normalize the image based on the new black and white points
    image = (image - black_point) / (white_point - black_point)
    
    return image

def process_depth_image(input_path, output_path, large_scale, fine_scale, boost, detail_threshold, spatial_sigma, range_sigma, black_point, white_point):
    try:
        depth_map = read_image(input_path)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Always extend dynamic range
    depth_map = extend_dynamic_range(depth_map, black_point, white_point)
    
    # First pass: reduce banding
    smoothed = reduce_banding(depth_map, large_scale, fine_scale, boost, detail_threshold)
    
    # Second pass: edge-preserving smoothing
    final = edge_preserving_smooth(smoothed, spatial_sigma, range_sigma)
    
    try:
        save_exr(output_path, final)
    except Exception as e:
        print(f"Error saving EXR file: {e}")
        sys.exit(1)


def reduce_banding(image, large_scale=15, fine_scale=3, boost=1.5, detail_threshold=0.02):
    large_smooth = cv2.bilateralFilter(image, d=large_scale, sigmaColor=0.1, sigmaSpace=large_scale)
    fine_smooth = cv2.bilateralFilter(image, d=fine_scale, sigmaColor=0.1, sigmaSpace=fine_scale)
    detail = image - fine_smooth
    boosted = fine_smooth + detail * boost
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

def main():
    parser = argparse.ArgumentParser(description="Depth Image Banding Reduction with HDR Extension")
    parser.add_argument("--i", "--input_file", dest="input_file", help="Input depth image file (PNG, JPG, TIFF, EXR, etc.)", default="input.png")
    parser.add_argument("--o", "--output_file", dest="output_file", help="Output EXR file", default="output.exr")
    parser.add_argument("--large_scale", type=int, default=15, help="Large scale bilateral filter size")
    parser.add_argument("--fine_scale", type=int, default=3, help="Fine scale bilateral filter size")
    parser.add_argument("--boost", type=float, default=1.5, help="Detail boost factor")
    parser.add_argument("--detail_threshold", type=float, default=0.02, help="Detail preservation threshold")
    parser.add_argument("--spatial_sigma", type=float, default=50.0, help="Spatial sigma for edge-preserving smoothing")
    parser.add_argument("--range_sigma", type=float, default=0.1, help="Range sigma for edge-preserving smoothing")
    parser.add_argument("--black_point", type=float, default=None, 
                        help="Black point for dynamic range extension. Range: [0.0, 1.0]. Default: None (no extension)")
    parser.add_argument("--white_point", type=float, default=None, 
                        help="White point for dynamic range extension. Range: [0.0, 1.0]. Must be greater than black point. Default: None (no extension)")
    
    args = parser.parse_args()
    
    print(f"Processing depth image: {args.input_file}")
    print(f"Output will be saved as: {args.output_file}")
    
    if args.black_point is not None and args.white_point is not None:
        if args.black_point < 0.0 or args.black_point >= 1.0 or args.white_point <= 0.0 or args.white_point > 1.0 or args.black_point >= args.white_point:
            print("Error: Invalid black or white point values. Please ensure 0.0 <= black_point < white_point <= 1.0")
            sys.exit(1)
        print(f"Extending dynamic range: Black point = {args.black_point}, White point = {args.white_point}")
    elif args.black_point is not None or args.white_point is not None:
        print("Error: Both black_point and white_point must be specified for dynamic range extension.")
        sys.exit(1)
    
    process_depth_image(args.input_file, args.output_file, 
                        args.large_scale, args.fine_scale, args.boost, args.detail_threshold,
                        args.spatial_sigma, args.range_sigma,
                        args.black_point, args.white_point)
    
    print(f"Black point: {args.black_point}")
    print(f"White point: {args.white_point}")
    
    process_depth_image(args.input_file, args.output_file, 
                        args.large_scale, args.fine_scale, args.boost, args.detail_threshold,
                        args.spatial_sigma, args.range_sigma,
                        args.black_point, args.white_point)
    
    print(f"Processed depth image saved as {args.output_file}")


if __name__ == "__main__":
    main()