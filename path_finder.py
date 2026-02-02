import numpy as np
from heapq import heappop, heappush
import rasterio
import os

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

def save_raster(data, meta, filename):
    meta.update(dtype="float32", count=1)
    with rasterio.open(filename, "w", **meta) as dst:
        dst.write(data, 1)

if __name__ == "__main__":
    input_file = "dmr5g_smrk.tif"  # Hardcoded file path
    with rasterio.open(input_file) as src:
        dem = src.read(1).astype("float32")
        meta = src.meta

        path = find_path_low_to_high(dem)
        path_raster = np.zeros_like(dem)
        for r, c in path:
            path_raster[r, c] = 1  # Označení cesty

        output_dir = "out"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        save_raster(path_raster, meta, f"{output_dir}/path_{os.path.basename(input_file)}")
        print("Trasa od nejnižšího k nejvyššímu pixelu byla vypočítána a uložena.")