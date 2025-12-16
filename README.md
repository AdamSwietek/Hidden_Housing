# HiddenHousing

Phase 1. is a change detection pipeline for building structures in the City of Los Angeles. It processes satellite imagery to identify how building footprints have changed over time.

***

## Processes

Load SatImg -> Extract Building Footprints -> Assign to Parcels -> Detect Change

### load_SATimg
- **Description**: Loads satellite imagery from various sources for a given geometry and year.
- **Sources**:
    - NearMaps
    - LARIAC
    - NAIPS
- **Details**:
    - Imagery is stored locally.
    - A function calls imagery by geometry and year using a directory path.
- **Function**:
    - `fetch_SAT(geom, year, source_dir) -> TIF`

### img2bfp: Extract Building Footprints
- **Description**: Extracts building footprints (BFP) from satellite imagery using different segmentation models.
- **Methods**:
    - SAM
    - ESRI
- **Function**:
    - `extract_BFP(satimg, method) -> geom`

### assign_PARCEL: Assign BFP to Parcels
- **Description**: Spatially joins the extracted building footprints to their corresponding land parcels.
- **Sources**:
    - Cached img2bfp results: `geom`
    - LA City parcel boundaries: `GeoDataFrame`
- **Function**:
    - `assign_to_parcel(bfp_geom, parcel_geom) -> GeoDataFrame`
- **Pipeline**:
    - Creates a "Parcel Building GeoDatabase" for each year.
    - `for yr in YEAR: assign_to_parcel(bfp_geom[yr], parcel_geom) -> GDB_for_year`

### detect_CHANGE: Detect Change Over Time
- **Description**: Identifies changes in building structures for each parcel by comparing footprints from two different time periods (t1 and t2).
- **Inputs**:
    - Parcel BFP GeoDataFrame for time t1
    - Parcel BFP GeoDataFrame for time t2
- **Process**:
    - For each parcel, compare the BFP geometry from t1 and t2.
    - Use geometric operations (e.g., intersection, difference) to quantify change.
    - Classify the change type (e.g., 'New Construction', 'Demolition', 'Addition', 'No Change').
- **Function**:
    - `detect_parcel_change(bfp_gdb_t1, bfp_gdb_t2) -> GeoDataFrame`
- **Output**:
    - A GeoDataFrame with parcel geometries and columns describing the change, such as `change_type` and `area_change_sqft`.

### load_BFP (Utility)
- **Description**: Utility for loading pre-existing or cached building footprint data for validation.
- **Sources**:
    - Cached `img2bfp` results
    - LARIAC boundary outlines
    - NearMaps products
    - OSMNX
- **Function**:
    - `load_PARCEL_BFP(geom, year) -> GeoDataFrame`


Structure
HiddenHousing/
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
│
├── data/
│   ├── 01_raw/
│   │   ├── parcel_boundaries/
│   │   └── satellite_imagery/
│   ├── 02_interim/
│   │   └── extracted_bfps/
│   ├── 03_processed/
│   │   └── parcel_bfp_gdb/
│   └── 04_results/
│       └── change_analysis/
│
├── notebooks/
│   ├── 1_data_exploration.ipynb
│   ├── 2_model_evaluation.ipynb
│   └── 3_results_visualization.ipynb
│
└── src/
    ├── __init__.py
    ├── data_loading.py
    ├── processing.py
    └── change_detection.py
