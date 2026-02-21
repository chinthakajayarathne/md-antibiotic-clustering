"""
Configuration for the Antibiotic Prescribing Clustering Analysis Pipeline.
"""
import os

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")

# Raw data path
PATH_TO_DATA = r"D:\Academic\MD Research 2025\raw data\2026_januaryPrescriptions_pseudonymised.csv"

# Intermediate data paths
ENCOUNTER_CLEAN_PATH = os.path.join(DATA_DIR, "encounter_level_clean.csv")
ENCOUNTER_PRESCRIBER_PATH = os.path.join(DATA_DIR, "encounter_level_with_prescriber.csv")
ENCOUNTER_CLUSTERED_PATH = os.path.join(DATA_DIR, "encounter_level_clustered.csv")

# ============================================================
# ANALYSIS PARAMETERS
# ============================================================

# Age strata definitions (upper bound in months, exclusive)
AGE_STRATA = [
    (0, 1, "neonate_0_27d"),        # 0-27 days ~ <1 month
    (1, 3, "infant_1_2m"),          # 1-2 months
    (3, 6, "infant_3_5m"),          # 3-5 months
    (6, 12, "infant_6_11m"),        # 6-11 months
    (12, 24, "toddler_12_23m"),     # 12-23 months
    (24, 60, "preschool_2_4y"),     # 2-4 years
    (60, 144, "child_5_11y"),       # 5-11 years
    (144, 216, "adolescent_12_17y"), # 12-17 years
    (216, 9999, "adult_18plus"),    # 18+
]

# Data cleaning thresholds
MIN_AGE_MONTHS = 0
MAX_AGE_MONTHS = 216
MIN_WEIGHT_KG = 0
MAX_WEIGHT_KG = 150

# Clustering parameters
K_RANGE = range(3, 9)  # k = 3 to 8
BOOTSTRAP_ITERATIONS = 20
BOOTSTRAP_SAMPLE_FRACTION = 0.80

# Polypharmacy threshold
POLYPHARMACY_THRESHOLD = 3

# Ensure output directories exist
for d in [OUTPUT_DIR, FIGURES_DIR, REPORTS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)
