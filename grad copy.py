import rasterio
import numpy as np

with rasterio.open("dmr5g_opalena.tif") as src:         #with = otevře a po skončení zavře soubor
    dem = src.read(1).astype("float32")      
    print(f"dem = pole s hodnotami nadmořské výšky, tvar: {dem.shape}, datový typ: {dem.dtype}")
    meta = src.meta
    print(f"Metadata: {meta}")
    # meta obsahuje informace o souboru (rozměry, datový typ, souřadnicový systém, atd.)
    cellsize = src.res[0] # velikost buňky v metrech (předpokládáme čtvercové buňky)
    print(f"Rozměry: {dem.shape}, velikost buňky: {cellsize} m")

#výpočet gradientu
dzdx, dzdy = np.gradient(dem, cellsize)
print("Gradient spočítán.")
print(f"dzdx: min {dzdx.min():.2f}, max {dzdx.max():.2f}, průměr {dzdx.mean():.2f}")

#výpočet sklonu ve stupních
slope = np.degrees(np.arctan(np.sqrt(dzdx**2 + dzdy**2)))
print("Sklon spočítán.")
print(f"Sklon: min {slope.min():.2f}, max {slope.max():.2f}, průměr {slope.mean():.2f}")

#uložení výstupu
meta.update(dtype="float32", count=1)

with rasterio.open("slope.tif", "w", **meta) as dst:
    dst.write(slope, 1)

print("Hotovo: slope.tif")
