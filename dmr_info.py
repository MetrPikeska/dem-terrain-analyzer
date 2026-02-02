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

def find_local_extrema(dem, window_size=3):
    """Najde lokální maxima a minima v DEM pomocí filtru."""
    rows, cols = dem.shape
    print(f"dem ma: {rows} radku a {cols} sloupcu")
    print(f"Finding local extrema in DEM of shape {dem.shape} with window size {window_size}")
    maxima = np.zeros_like(dem, dtype=bool)
    minima = np.zeros_like(dem, dtype=bool)

    offset = window_size // 2

    for i in range(offset, rows - offset):
        for j in range(offset, cols - offset):
            # Výřez okolí
            window = dem[i - offset:i + offset + 1, j - offset:j + offset + 1]
            center = dem[i, j]

            #je to maximum??
            if center == np.max(window):
                maxima[i, j] = True

            #je to minimum??
            if center == np.min(window):
                minima[i, j] = True
    return maxima, minima

def calculate_flow_direction(dem):
    """Vypočítá směr, kterým by tekla voda (D8 algoritmus)"""
    rows, cols = dem.shape
    flow_dir = np.zeros_like(dem, dtype=int)
    
    # Kódy směrů (mocniny 2)
    # 32  64  128
    # 16   X   1
    # 8    4   2
    directions = [(0, 1, 1), (-1, 1, 2), (-1, 0, 4), (-1, -1, 8),
                  (0, -1, 16), (1, -1, 32), (1, 0, 64), (1, 1, 128)]
    
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            current_elevation = dem[i, j]
            max_slope = -999999
            direction = 0
            
            # Najdi směr s největším sklonem
            for di, dj, code in directions:
                neighbor_elevation = dem[i + di, j + dj]
                slope = current_elevation - neighbor_elevation
                
                if slope > max_slope:
                    max_slope = slope
                    direction = code
            
            flow_dir[i, j] = direction
    
    return flow_dir

def detect_ridges_valleys(curvature, threshold=0.1):
    """Detekuje hřbety (kladné zakřivení) a údolí (záporné)"""
    rows, cols = curvature.shape
    ridges = np.zeros_like(curvature, dtype=bool)
    valleys = np.zeros_like(curvature, dtype=bool)
    
    ridge_count = 0
    valley_count = 0
    
    for i in range(rows):
        for j in range(cols):
            curv = curvature[i, j]
            
            if curv > threshold:
                ridges[i, j] = True
                ridge_count += 1
            elif curv < -threshold:
                valleys[i, j] = True
                valley_count += 1
    
    print(f"Nalezeno hřbetů: {ridge_count}")
    print(f"Nalezeno údolí: {valley_count}")
    
    return ridges, valleys

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

    # Lokální extrémy
    local_extrema = find_local_extrema(dem)
    save_raster(local_extrema[0].astype("float32"), meta, f"{output_dir}/local_maxima_{out_name}.tif")
    print("Lokální maxima nalezena a uložena.")
    save_raster(local_extrema[1].astype("float32"), meta, f"{output_dir}/local_minima_{out_name}.tif")
    print("Lokální minima nalezena a uložena.")

    # Směr toku
    flow_direction = calculate_flow_direction(dem)
    save_raster(flow_direction.astype("float32"), meta, f"{output_dir}/flow_direction_{out_name}.tif")
    print("Směr toku spočítán a uložen.")  

    # Detekce hřbetů a údolí
    ridges, valleys = detect_ridges_valleys(curvature)
    save_raster(ridges.astype("float32"), meta, f"{output_dir}/ridges_{out_name}.tif")
    print("Hřbety detekovány a uloženy.")
    save_raster(valleys.astype("float32"), meta, f"{output_dir}/valleys_{out_name}.tif")
    print("Údolí detekována a uložena.")
    





