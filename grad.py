import rasterio
import numpy as np

# 1️⃣ otevření DMR
with rasterio.open("dmr5g_opalena.tif") as src:
    dem = src.read(1).astype("float32")
    meta = src.meta
    cellsize = src.res[0]

# 2️⃣ výpočet gradientu
dzdx, dzdy = np.gradient(dem, cellsize)

# 3️⃣ výpočet sklonu ve stupních
slope = np.degrees(np.arctan(np.sqrt(dzdx**2 + dzdy**2)))

# 4️⃣ uložení výstupu
meta.update(dtype="float32", count=1)

with rasterio.open("slope.tif", "w", **meta) as dst:
    dst.write(slope, 1)

print("Hotovo: slope.tif")
