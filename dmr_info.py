import rasterio
import numpy as np
import os
import scipy.ndimage as ndimage
from heapq import heappop, heappush

def apply_high_pass_filter(dem):
    kernel = np.array([[-1, -1, -1],
                       [-1,  8, -1],
                       [-1, -1, -1]])
    from scipy.ndimage import convolve
    high_pass = convolve(dem, kernel, mode='nearest')
    return high_pass

def calculate_slope(dzdx, dzdy):
    return np.degrees(np.arctan(np.sqrt(dzdx**2 + dzdy**2)))

def calculate_aspect(dzdx, dzdy):
    aspect = np.degrees(np.arctan2(-dzdy, dzdx))
    return np.where(aspect < 0, 360 + aspect, aspect)

def calculate_curvature(dzdx, dzdy):
    d2zdx2 = np.gradient(dzdx, axis=1)  # Druhá derivace ve směru X
    d2zdy2 = np.gradient(dzdy, axis=0)  # Druhá derivace ve směru Y
    return d2zdx2 + d2zdy2  # Celkové zakřivení

def calculate_hillshade(dzdx, dzdy, altitude=45, azimuth=315):
    slope = np.arctan(np.sqrt(dzdx**2 + dzdy**2))
    aspect = np.arctan2(-dzdy, dzdx)
    altitude_rad = np.radians(altitude)
    azimuth_rad = np.radians(azimuth)
    shaded = (np.sin(altitude_rad) * np.cos(slope) +
              np.cos(altitude_rad) * np.sin(slope) * np.cos(azimuth_rad - aspect))
    return np.clip(shaded, 0, 1)

def save_raster(data, meta, filename):
    meta.update(dtype="float32", count=1)
    with rasterio.open(filename, "w", **meta) as dst:
        dst.write(data, 1)

# Hlavní část skriptu
input_file = "dmr5g_opalena.tif"  # Zadejte cestu k vašemu DEM souboru
out_name = os.path.splitext(os.path.basename(input_file))[0]

with rasterio.open(input_file) as src:
    dem = src.read(1).astype("float32")
    meta = src.meta
    cellsize = src.res[0]

    output_dir = "out"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Výpočet gradientů
    dzdx, dzdy = np.gradient(dem, cellsize)

    # Sklon
    slope = calculate_slope(dzdx, dzdy)
    save_raster(slope, meta, f"{output_dir}/slope_{out_name}.tif")
    print("Sklon spočítán a uložen.")

    # Aspekt
    aspect = calculate_aspect(dzdx, dzdy)
    save_raster(aspect, meta, f"{output_dir}/aspect_{out_name}.tif")
    print("Aspekt spočítán a uložen.")

    # Zakřivení
    curvature = calculate_curvature(dzdx, dzdy)
    save_raster(curvature, meta, f"{output_dir}/curvature_{out_name}.tif")
    print("Zakřivení spočítáno a uloženo.")

    # Hillshade
    hillshade = calculate_hillshade(dzdx, dzdy)
    save_raster(hillshade, meta, f"{output_dir}/hillshade_{out_name}.tif")
    print("Hillshade spočítán a uložen.")

    # High-pass filter
    high_pass = apply_high_pass_filter(dem)
    save_raster(high_pass, meta, f"{output_dir}/high_pass_{out_name}.tif")
    print("High-pass filtr aplikován a uložen.")



