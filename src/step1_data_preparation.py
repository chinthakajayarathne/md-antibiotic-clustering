"""
Step 1: Data Preparation & Exploratory Data Analysis
=====================================================
Data is already encounter-level from SQL extraction.
This script:
- Loads the CSV
- Adds remaining derived variables (monotherapy, combination, polypharmacy)
- Cleans age/weight outliers
- Prints EDA statistics
- Creates visualizations
- Saves encounter_level_clean.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import (
    PATH_TO_DATA, ENCOUNTER_CLEAN_PATH, FIGURES_DIR,
    AGE_STRATA, MIN_AGE_MONTHS, MAX_AGE_MONTHS,
    MIN_WEIGHT_KG, MAX_WEIGHT_KG, POLYPHARMACY_THRESHOLD
)

plt.style.use("seaborn-v0_8-whitegrid")


def load_data(path):
    """Load the encounter-level CSV."""
    print("=" * 60)
    print("STEP 1: DATA PREPARATION & EXPLORATORY ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(path, low_memory=False)

    # Normalize column names for pseudonymised data
    rename_map = {
        "patient_pseudo_id": "patient_id",
        "prescriber_pseudo_id": "prescriber_id",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    print(f"\nLoaded: {df.shape[0]} encounters, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string())
    print(f"\nData types:\n{df.dtypes}")
    return df


def add_derived_variables(df):
    """Add antibiotic_monotherapy, antibiotic_combination, polypharmacy_flag."""
    print("\n--- Adding derived variables ---")

    df["antibiotic_monotherapy"] = (df["num_antibiotics"] == 1).astype(int)
    df["antibiotic_combination"] = (df["num_antibiotics"] >= 2).astype(int)
    df["polypharmacy_flag"] = (
        df["num_distinct_drugs"] >= POLYPHARMACY_THRESHOLD
    ).astype(int)

    print(f"  antibiotic_monotherapy: {df['antibiotic_monotherapy'].sum()} encounters")
    print(f"  antibiotic_combination: {df['antibiotic_combination'].sum()} encounters")
    print(f"  polypharmacy_flag: {df['polypharmacy_flag'].sum()} encounters")
    return df


def clean_data(df):
    """Apply data cleaning rules for age and weight."""
    print("\n--- Cleaning data ---")
    n_before = len(df)

    # Parse DateTimeOfVisit
    df["DateTimeOfVisit"] = pd.to_datetime(df["DateTimeOfVisit"], errors="coerce")

    # Age cleaning
    mask_age = (df["age_months"] >= MIN_AGE_MONTHS) & (df["age_months"] <= MAX_AGE_MONTHS)
    n_age_removed = (~mask_age).sum()
    df = df[mask_age].copy()
    print(f"  Removed {n_age_removed} encounters with invalid age")

    # Weight cleaning: set invalid to NaN, keep missing as NaN
    invalid_weight = (
        (df["PatientWeight"] < MIN_WEIGHT_KG) | (df["PatientWeight"] > MAX_WEIGHT_KG)
    )
    n_invalid_wt = invalid_weight.sum()
    df.loc[invalid_weight, "PatientWeight"] = np.nan
    print(f"  Set {n_invalid_wt} invalid weight values to NaN")
    print(f"  Weight missing/NaN: {df['PatientWeight'].isna().sum()} encounters")

    # Standardize drug_groups text
    if "drug_groups" in df.columns:
        df["drug_groups"] = df["drug_groups"].astype(str).str.strip()

    print(f"  Final dataset: {len(df)} encounters (removed {n_before - len(df)})")
    return df


def print_eda(df):
    """Print exploratory statistics."""
    print("\n" + "=" * 60)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    total = len(df)
    ab_n = df["has_antibiotic"].sum()
    ab_rate = ab_n / total * 100

    print(f"\nTotal encounters:          {total}")
    print(f"Unique patients:           {df['patient_id'].nunique()}")
    print(f"Unique prescribers:        {df['prescriber_id'].nunique()}")
    print(f"Date range:                {df['DateTimeOfVisit'].min()} to {df['DateTimeOfVisit'].max()}")
    print(f"\nAntibiotic rate:           {ab_rate:.1f}% ({ab_n}/{total})")
    print(f"Monotherapy rate (of AB):  {df['antibiotic_monotherapy'].sum()}/{ab_n} = "
          f"{df['antibiotic_monotherapy'].sum() / ab_n * 100:.1f}%" if ab_n > 0 else "N/A")
    print(f"Combination rate (of AB):  {df['antibiotic_combination'].sum()}/{ab_n} = "
          f"{df['antibiotic_combination'].sum() / ab_n * 100:.1f}%" if ab_n > 0 else "N/A")
    print(f"Polypharmacy rate:         {df['polypharmacy_flag'].mean() * 100:.1f}%")
    print(f"Mean drugs/encounter:      {df['num_distinct_drugs'].mean():.2f}")

    print("\n--- Antibiotic rate by age stratum ---")
    age_order = [s[2] for s in AGE_STRATA]
    age_ab = df.groupby("age_stratum").agg(
        n=("OPDID", "count"),
        ab_rate=("has_antibiotic", "mean"),
    ).reindex(age_order).dropna()
    age_ab["ab_rate_pct"] = (age_ab["ab_rate"] * 100).round(1)
    print(age_ab[["n", "ab_rate_pct"]].to_string())

    print("\n--- Distribution of num_distinct_drugs ---")
    print(df["num_distinct_drugs"].describe().to_string())


def create_visualizations(df):
    """Create and save EDA charts."""
    print("\n--- Creating visualizations ---")

    age_order = [s[2] for s in AGE_STRATA]

    # 1. Encounters by age group
    fig, ax = plt.subplots(figsize=(10, 6))
    counts = df["age_stratum"].value_counts().reindex(age_order).dropna()
    counts.plot(kind="bar", ax=ax, color="steelblue", edgecolor="black")
    ax.set_title("Number of Encounters by Age Group", fontsize=14)
    ax.set_xlabel("Age Stratum")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/01_encounters_by_age.png", dpi=150)
    plt.close()

    # 2. Antibiotic pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    ab_counts = df["has_antibiotic"].value_counts().sort_index()
    ax.pie(ab_counts, labels=["No Antibiotic", "Has Antibiotic"],
           colors=["#66b3ff", "#ff6666"], autopct="%1.1f%%",
           startangle=90, textprops={"fontsize": 12})
    ax.set_title("Antibiotic vs Non-Antibiotic Encounters", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/02_antibiotic_pie.png", dpi=150)
    plt.close()

    # 3. Drugs per encounter histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    max_drugs = int(df["num_distinct_drugs"].max())
    df["num_distinct_drugs"].plot(
        kind="hist", bins=range(1, max_drugs + 2),
        ax=ax, color="steelblue", edgecolor="black", align="left"
    )
    ax.set_title("Distribution of Drugs per Encounter", fontsize=14)
    ax.set_xlabel("Number of Distinct Drugs")
    ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/03_drugs_histogram.png", dpi=150)
    plt.close()

    # 4. Antibiotics by age stratum (box plot)
    fig, ax = plt.subplots(figsize=(12, 6))
    ab_data = df[df["has_antibiotic"] == 1]
    if len(ab_data) > 0:
        present = [a for a in age_order if a in ab_data["age_stratum"].values]
        sns.boxplot(data=ab_data, x="age_stratum", y="num_antibiotics",
                    order=present, ax=ax)
    ax.set_title("Antibiotics per Encounter by Age (AB encounters only)", fontsize=14)
    ax.set_xlabel("Age Stratum")
    ax.set_ylabel("Number of Antibiotics")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/04_antibiotics_by_age_box.png", dpi=150)
    plt.close()

    # 5. Antibiotic rate by age stratum (bar)
    fig, ax = plt.subplots(figsize=(10, 6))
    ab_by_age = df.groupby("age_stratum")["has_antibiotic"].mean().reindex(age_order).dropna() * 100
    ab_by_age.plot(kind="bar", ax=ax, color="salmon", edgecolor="black")
    ax.set_title("Antibiotic Prescribing Rate by Age Group", fontsize=14)
    ax.set_xlabel("Age Stratum")
    ax.set_ylabel("Antibiotic Rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/05_ab_rate_by_age.png", dpi=150)
    plt.close()

    print(f"  Saved 5 figures to {FIGURES_DIR}/")


def run():
    """Execute Step 1."""
    df = load_data(PATH_TO_DATA)
    df = add_derived_variables(df)
    df = clean_data(df)
    print_eda(df)
    create_visualizations(df)
    df.to_csv(ENCOUNTER_CLEAN_PATH, index=False)
    print(f"\nSaved: {ENCOUNTER_CLEAN_PATH}")
    return df


if __name__ == "__main__":
    run()
