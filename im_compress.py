#!/usr/bin/env python3

import os
import io
from PIL import Image
import argparse

def compress_to_target_size(input_path, output_path, target_size_kb, max_quality=95, min_quality=10):
    img = Image.open(input_path)
    img_format = "JPEG" if img.mode in ("RGB", "L") else "PNG"
    img = img.convert("RGB") if img_format == "JPEG" else img  # PNG can keep alpha

    # Binary search for the right quality
    best_quality = min_quality
    best_output = None
    low = min_quality
    high = max_quality

    while low <= high:
        mid = (low + high) // 2
        buffer = io.BytesIO()
        img.save(buffer, format=img_format, quality=mid, optimize=True)
        size_kb = len(buffer.getvalue()) / 1024

        if size_kb <= target_size_kb:
            best_quality = mid
            best_output = buffer.getvalue()
            low = mid + 1
        else:
            high = mid - 1

    if best_output:
        with open(output_path, "wb") as f:
            f.write(best_output)
        print(f"Compressed to {output_path} (Quality={best_quality}, Size={os.path.getsize(output_path)/1024:.1f}KB)")
    else:
        print(f"Could not compress {input_path} below {target_size_kb}KB")

def main():
    parser = argparse.ArgumentParser(description="Compress image to target size in KB.")
    parser.add_argument("input", help="Input image or folder")
    parser.add_argument("-o", "--output", default="compressed", help="Output directory")
    parser.add_argument("-s", "--size", type=int, required=True, help="Target max size in KB (e.g. 200 for 200KB)")

    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    def process(file_path):
        if file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            output_file = os.path.join(args.output, os.path.basename(file_path))
            compress_to_target_size(file_path, output_file, args.size)

    if os.path.isdir(args.input):
        for file in os.listdir(args.input):
            process(os.path.join(args.input, file))
    else:
        process(args.input)

if __name__ == "__main__":
    main()
