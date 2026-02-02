import rasterio
import numpy as np

with rasterio.open("dmr5g_opalena.tif") as src:         #with = otevře a po skončení zavře soubor
    dem = src.read(1).astype("float32")
    # ted jsem načetl data do pole dem
    meta = src.meta
    # meta
    cellsize = src.res[0]
    print(f"Rozměry: {dem.shape}, velikost buňky: {cellsize} m")

#výpočet gradientu
dzdx, dzdy = np.gradient(dem, cellsize)

#výpočet sklonu ve stupních
slope = np.degrees(np.arctan(np.sqrt(dzdx**2 + dzdy**2)))

#uložení výstupu
meta.update(dtype="float32", count=1)

with rasterio.open("slope.tif", "w", **meta) as dst:
    dst.write(slope, 1)

print("Hotovo: slope.tif")
