# notebooks/tasks

Pipeline notebooks for the Hidden Housing project. Each notebook is a self-contained step in the data processing chain, using `src/` modules for all heavy lifting.

## Notebooks

| Notebook | Status | Output |
|----------|--------|--------|
| `00_generate_lacity_assessor_lariac.ipynb` | ✅ complete | `data/processed/assessor_lariac.gpkg` — master parcel×building dataset, 3 year layers (2014, 2017, 2020) |
| `generate_lacity_adp.ipynb` | ✅ complete | `data/04_results/lacity_apd_building_features.gpkg` — citywide ADP building features (parallel run) |
| `01_lariac_symdiff.ipynb` | ✅ complete | `data/04_results/lariac_symdiff.gpkg` — per-AIN temporal change classification across epochs |
| `03_analysis_udu.ipynb` | ✅ complete | exploratory — UDU vs non-UDU building feature distributions |
| `02_lidar.ipynb` | 🔲 in progress | TBD — LiDAR point cloud processing via MeshCity |

## Task checklist

- [x] Ingest and index LARIAC, Assessor, Landbase datasets → AIN-keyed
- [x] Extract per-building and per-parcel morphology metrics (FAR, BAR, setback, n buildings)
- [x] Build master assessor×LARIAC GeoPackage with thin-connection split and per-AIN aggregation
- [x] Citywide ADP building features (parallel neighborhood pipeline)
- [x] LARIAC temporal symdiff: epoch alignment, change classification, added/removed geometry
- [x] UDU vs non-UDU distribution analysis
- [ ] LiDAR integration (MeshCity)
- [ ] Extension vs standalone classification (geometric: contiguous vs detached new area)
- [ ] Temporal change × UDU join — compare change rates across UDU and non-UDU parcels
- [ ] ML prediction model (Phase 2)
- [ ] DiD causal impact estimation (Phase 3)

## Key parameters

All pipeline notebooks share these conventions:

- **CRS**: EPSG:2229 (CA State Plane, feet) for storage; EPSG:32611 (UTM Zone 11N, metres) for geometry operations
- **AIN**: Assessor Identification Number — primary join key across all datasets
- **Epochs**: 2014, 2017, 2020 (LARIAC survey years)
- **Thin-connection split**: erosion-dilation at 1 m threshold with mitre cap style before AIN assignment
- **Epoch alignment**: region-wide mean centroid shift across all common AINs, applied in UTM
