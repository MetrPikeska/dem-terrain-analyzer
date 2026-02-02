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
with rasterio.open("dmr5g_smrk.tif") as src:
    dem = src.read(1).astype("float32")
    meta = src.meta
    cellsize = src.res[0]
    out_name = input("Zadejte název vstupního souboru (např. dmr5g_smrk.tif): ")

    outpust_dir = "out"
    if not os.path.exists(outpust_dir):
        os.makedirs(outpust_dir)

    # Výpočet gradientů
    dzdx, dzdy = np.gradient(dem, cellsize)

    # Sklon
    slope = calculate_slope(dzdx, dzdy)
    save_raster(slope, meta, f"out/slope_{out_name}.tif")
    print("Sklon spočítán a uložen.")

    # Aspekt
    aspect = calculate_aspect(dzdx, dzdy)
    save_raster(aspect, meta, f"out/aspect_{out_name}.tif")
    print("Aspekt spočítán a uložen.")

    # Zakřivení
    curvature = calculate_curvature(dzdx, dzdy)
    save_raster(curvature, meta, f"out/curvature_{out_name}.tif")
    print("Zakřivení spočítáno a uloženo.")

    # Hillshade
    hillshade = calculate_hillshade(dzdx, dzdy)
    save_raster(hillshade, meta, f"out/hillshade_{out_name}.tif")
    print("Hillshade spočítán a uložen.")

    # High-pass filter
    high_pass = apply_high_pass_filter(dem)
    save_raster(high_pass, meta, f"out/high_pass_{out_name}.tif")
    print("High-pass filtr aplikován a uložen.")

    # Find and save the path
    def find_path_low_to_high(dem):
        rows, cols = dem.shape
        start = np.unravel_index(np.argmin(dem), dem.shape)  # Pixel s nejnižší hodnotou
        end = np.unravel_index(np.argmax(dem), dem.shape)  # Pixel s nejvyšší hodnotou

        # Priority queue for Dijkstra's algorithm
        pq = [(0, start)]  # (cost, (row, col))
        visited = set()
        prev = {}
        costs = {start: 0}

        while pq:
            cost, current = heappop(pq)
            if current in visited:
                continue
            visited.add(current)

            if current == end:
                break

            row, col = current
            neighbors = [
                (row + dr, col + dc)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4-směrné sousedy
                if 0 <= row + dr < rows and 0 <= col + dc < cols
            ]

            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                nrow, ncol = neighbor
                diff = abs(dem[nrow, ncol] - dem[row, col])
                new_cost = cost + diff
                if neighbor not in costs or new_cost < costs[neighbor]:
                    costs[neighbor] = new_cost
                    heappush(pq, (new_cost, neighbor))
                    prev[neighbor] = current

        # Rekonstrukce cesty
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = prev.get(current)

        return path[::-1]  # Reverse path

    path = find_path_low_to_high(dem)
    path_raster = np.zeros_like(dem)
    for r, c in path:
        path_raster[r, c] = 1  # Označení cesty
    save_raster(path_raster, meta, f"out/path_{out_name}.tif")
    print("Trasa od nejnižšího k nejvyššímu pixelu byla vypočítána a uložena.")

