import rasterio
import numpy as np
import os

# Funkce pro analýzy
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
with rasterio.open("dmr5g_opalena.tif") as src:
    dem = src.read(1).astype("float32")
    meta = src.meta
    cellsize = src.res[0]

    outpust_dir = "out"
    if not os.path.exists(outpust_dir):
        os.makedirs(outpust_dir)

    # Výpočet gradientů
    dzdx, dzdy = np.gradient(dem, cellsize)

    # Sklon
    slope = calculate_slope(dzdx, dzdy)
    save_raster(slope, meta, "out/slope.tif")
    print("Sklon spočítán a uložen.")

    # Aspekt
    aspect = calculate_aspect(dzdx, dzdy)
    save_raster(aspect, meta, "out/aspect.tif")
    print("Aspekt spočítán a uložen.")

    # Zakřivení
    curvature = calculate_curvature(dzdx, dzdy)
    save_raster(curvature, meta, "out/curvature.tif")
    print("Zakřivení spočítáno a uloženo.")

    # Hillshade
    hillshade = calculate_hillshade(dzdx, dzdy)
    save_raster(hillshade, meta, "out/hillshade.tif")
    print("Hillshade spočítán a uložen.")

