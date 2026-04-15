
# Hidden Housing — Task Checklist

## 1. Data ingestion & spatial indexing

- [x] **LARIAC** — `load_laraic()` in `src/geoadmin.py`
- [x] **Assessor** — `load_assessor_parcels_bygeom()`, `load_parcels_by_AIN()`, `csv_to_sqlite()` in `src/geoadmin.py` / `src/io.py`
- [x] **Landbase** — `get_landbase_bymask()`, `process_parcels_bymask()` in `src/geoadmin.py`
- [x] **Map all datasets to AIN** — `merge_assessor_landbase()` + `unary_join_to_parcels()` in `src/geoadmin.py` / `src/metrics.py`
- [ ] **LiDAR** — in progress, will use MeshCity (`02_lidar.ipynb`)

## 2. Building feature extraction

- [x] **Per-building metrics** (vol, area, shape indices) — `get_building_lvl_feats()`, `extract_building_features()` in `src/metrics.py`
- [x] **Per-parcel metrics** (FAR, built area ratio, setback, n buildings) — `unary_join_to_parcels()`, `extract_assessor_metrics()`, `extract_building_to_parcel_feats()` in `src/metrics.py`
- [x] **Citywide ADP feature file** — `generate_lacity_adp.ipynb` → `data/04_results/lacity_apd_building_features.gpkg`
- [x] **Master assessor×LARIAC dataset** — `00_generate_lacity_assessor_lariac.ipynb` → `data/processed/assessor_lariac.gpkg` (3 year layers: 2014, 2017, 2020); includes thin-connection split

## 3. Temporal change detection

- [x] **LARIAC epoch symdiff** — `01_lariac_symdiff.ipynb` → `data/04_results/lariac_symdiff.gpkg`
  - thin-connection split (erosion-dilation, UTM, mitre cap)
  - region-wide epoch alignment (mean centroid shift over all common AINs)
  - per-AIN: `area_net`, `n_delta`, `change_type` (new_parcel / demolished / added_structure / removed_structure / extended / reduced / no_change)
  - symdiff geometry layers (added/removed polygons) when `STORE_SYMDIFF=True`
- [ ] **Extension vs standalone** — geometric classification of added area (contiguous vs detached new footprint); TBD

## 4. Analysis

- [x] **UDU vs non-UDU distribution** — `03_analysis_udu.ipynb`; requires `lacity_apd_building_features.gpkg`
- [ ] **Temporal change × UDU** — join symdiff output to known UDU parcels; compare change rates
- [ ] **ML prediction model** — Phase 2 (TBD)
- [ ] **DiD causal impact** — Phase 3 (TBD)
