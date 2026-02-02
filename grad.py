import rasterio
import numpy as np

with rasterio.open("dmr5g_opalena.tif") as src:         #with = otevře a po skončení zavře soubor
    dem = src.read(1).astype("float32")      
    print(f"dem = {dem.shape}, datový typ: {dem.dtype}")
    meta = src.meta
    print("Metadata loaded.")
    #print(f"Metadata: {meta}")
    cellsize = src.res[0]
    print(f"Cell size extracted: {cellsize}")
    celltype = "neznámý" 
    if cellsize >= 2:
        celltype = "DMR 5G 2m"
    else:
        print("Unknown cell type")
    print(f"Rozměry: {dem.shape}, velikost buňky: {cellsize:.2f} m, typ buňky: {celltype}")

#vypocet statistik
print(f"DEM: min {dem.min():.2f}, max {dem.max():.2f}, průměr {dem.mean():.2f}")

#výpočet gradientu
dzdx, dzdy = np.gradient(dem, cellsize)
# print("Gradient spočítán.")
# print(f"dzdx: min {dzdx.min():.2f}, max {dzdx.max():.2f}, průměr {dzdx.mean():.2f}")
# #výpočet sklonu ve stupních
# slope = np.degrees(np.arctan(np.sqrt(dzdx**2 + dzdy**2)))
# print("Sklon spočítán.")
# print(f"Sklon: min {slope.min():.2f}, max {slope.max():.2f}, průměr {slope.mean():.2f}")

# #uložení výstupu
# meta.update(dtype="float32", count=1)

# with rasterio.open("slope.tif", "w", **meta) as dst:
#     dst.write(slope, 1)

# print("Hotovo: slope.tif")
