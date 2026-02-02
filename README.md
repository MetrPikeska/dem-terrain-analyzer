# DEM Terrain Analyzer

Nástroj pro analýzu digitálních modelů terénu (DEM) s implementací optimalizovaného A* algoritmu pro hledání optimální cesty mezi nejnižším a nejvyšším bodem v terénu.

## 📋 Popis

Tento projekt analyzuje rastrová data digitálních modelů terénu a vypočítává optimální cestu od nejnižšího po nejvyšší bod s minimalizací výškových rozdílů. Využívá pokročilý A* algoritmus s Euklidovskou heuristikou pro efektivní výpočet.

## ✨ Funkce

- **A* Pathfinding** - Optimalizovaný algoritmus pro rychlé hledání cesty
- **8-směrné pohyby** - Podporuje diagonální pohyb pro přirozenější trasy
- **Heuristická optimalizace** - Výrazně rychlejší než klasický Dijkstra algoritmus
- **Rastrový export** - Ukládání výsledků ve formátu GeoTIFF
- **Automatická detekce** - Nalezení extrémních bodů (min/max) v terénu

## 🚀 Instalace

### Požadavky

- Python 3.7+
- NumPy
- Rasterio

### Instalace závislostí

```bash
pip install numpy rasterio
```

## 📖 Použití

### Základní použití

```python
from path_finder import find_path_low_to_high
import rasterio

# Načtení DEM
with rasterio.open("input_dem.tif") as src:
    dem = src.read(1).astype("float32")
    
    # Výpočet cesty
    path = find_path_low_to_high(dem)
    
    print(f"Nalezena cesta s {len(path)} body")
```

### Spuštění skriptu

```bash
python path_finder.py
```

Skript zpracuje soubor `dmr5g_opalena.tif` a uloží výsledek do složky `out/`.

## 🔧 Konfigurace

Upravte vstupní soubor v `path_finder.py`:

```python
input_file = "your_dem_file.tif"  # Cesta k vašemu DEM souboru
```

## 📊 Výstup

Skript vytvoří:
- `out/path_*.tif` - Rastrový soubor s vyznačenou cestou (hodnota 1 = cesta, 0 = ostatní)

## 🧮 Algoritmus

### A* s optimalizacemi

1. **Heuristika**: Euklidovská vzdálenost k cíli
2. **Kostní funkce**: Absolutní výškový rozdíl × vzdálenost
3. **Datové struktury**: NumPy arrays pro O(1) přístup
4. **Směry pohybu**: 8 směrů (4 kardinální + 4 diagonální)

### Složitost

- **Časová**: O(n log n) kde n je počet pixelů
- **Prostorová**: O(n) pro ukládání costs a visited

## 📈 Výkon

Optimalizace oproti původní implementaci:
- **5-20× rychlejší** výpočet v závislosti na velikosti DEM
- Použití numpy arrays místo Python dictionary
- A* heuristika redukuje prohledávaný prostor
- Boolean numpy array pro visited místo Python set

## 🎓 Vzdělávací účel

Tento projekt byl vytvořen pro sebevzdělávací účely s následujícími cíli:

- Pochopení grafových algoritmů (A*, Dijkstra)
- Práce s geoprostorovými daty
- Optimalizace Python kódu
- Použití NumPy a Rasterio knihoven

## 📝 Licence

Tento projekt je vytvořen pro vzdělávací účely.

## 🤝 Přispívání

Návrhy na vylepšení jsou vítány! Projekt slouží především k učení a experimentování.

## 📧 Kontakt

Pro dotazy nebo návrhy vytvořte issue v tomto repozitáři.

---

**Poznámka**: Pro produkční použití doporučujeme další validaci vstupních dat a error handling.
