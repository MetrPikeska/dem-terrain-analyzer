import numpy as np
from heapq import heappop, heappush
import rasterio
import os

def find_path_low_to_high(dem):
    rows, cols = dem.shape
    start = np.unravel_index(np.argmin(dem), dem.shape)
    end = np.unravel_index(np.argmax(dem), dem.shape)

    # A* heuristika - Euklidovská vzdálenost
    def heuristic(pos):
        return np.sqrt((pos[0] - end[0])**2 + (pos[1] - end[1])**2)

    # Použití numpy array místo dictionary pro rychlejší přístup
    costs = np.full((rows, cols), np.inf, dtype=np.float32)
    costs[start] = 0
    
    visited = np.zeros((rows, cols), dtype=bool)
    prev = {}

    # Priority queue: (f_score, cost, (row, col))
    pq = [(heuristic(start), 0, start)]

    # Předpočítání sousedů (8-směrné pro kratší cesty)
    neighbors_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                         (0, 1), (1, -1), (1, 0), (1, 1)]

    while pq:
        _, cost, current = heappop(pq)
        
        if visited[current]:
            continue
            
        visited[current] = True

        if current == end:
            break

        row, col = current
        
        for dr, dc in neighbors_offsets:
            nrow, ncol = row + dr, col + dc
            
            # Bounds check
            if not (0 <= nrow < rows and 0 <= ncol < cols):
                continue
                
            if visited[nrow, ncol]:
                continue
            
            neighbor = (nrow, ncol)
            
            # Diagonální pohyb má větší vzdálenost
            distance = 1.414 if (dr != 0 and dc != 0) else 1.0
            diff = abs(dem[nrow, ncol] - dem[row, col])
            new_cost = cost + diff * distance
            
            if new_cost < costs[nrow, ncol]:
                costs[nrow, ncol] = new_cost
                f_score = new_cost + heuristic(neighbor)
                heappush(pq, (f_score, new_cost, neighbor))
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
    input_file = "dmr5g_opalena.tif"  # Hardcoded file path
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