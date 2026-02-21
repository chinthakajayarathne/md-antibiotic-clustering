"""
Step 2: Prescriber Behaviour Analysis
=======================================
- Calculate prescriber-level metrics
- Merge back to encounter level
- Visualize prescriber behaviour
- Save encounter_level_with_prescriber.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import ENCOUNTER_CLEAN_PATH, ENCOUNTER_PRESCRIBER_PATH, FIGURES_DIR

plt.style.use("seaborn-v0_8-whitegrid")


def run():
    print("=" * 60)
    print("STEP 2: PRESCRIBER BEHAVIOUR ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(ENCOUNTER_CLEAN_PATH, low_memory=False)
    print(f"\nLoaded: {len(df)} encounters")
    print(f"Unique prescribers: {df['prescriber_id'].nunique()}")

    # ------------------------------------------------------------------
    # Calculate prescriber-level metrics
    # ------------------------------------------------------------------
    print("\n--- Computing prescriber metrics ---")
    prescriber = df.groupby("prescriber_id").agg(
        prescriber_total_encounters=("OPDID", "count"),
        prescriber_ab_encounters=("has_antibiotic", "sum"),
        prescriber_sum_antibiotics=("num_antibiotics", "sum"),
        prescriber_polypharmacy_encounters=("polypharmacy_flag", "sum"),
    ).reset_index()

    prescriber["prescriber_antibiotic_rate"] = (
        prescriber["prescriber_ab_encounters"] / prescriber["prescriber_total_encounters"]
    ).round(4)
    prescriber["prescriber_mean_num_antibiotics"] = (
        prescriber["prescriber_sum_antibiotics"] / prescriber["prescriber_total_encounters"]
    ).round(4)
    prescriber["prescriber_polypharmacy_rate"] = (
        prescriber["prescriber_polypharmacy_encounters"] / prescriber["prescriber_total_encounters"]
    ).round(4)

    print(f"\nPrescriber summary statistics:")
    print(prescriber[[
        "prescriber_antibiotic_rate",
        "prescriber_mean_num_antibiotics",
        "prescriber_polypharmacy_rate",
    ]].describe().to_string())

    # ------------------------------------------------------------------
    # Top 10 prescribers by volume
    # ------------------------------------------------------------------
    print("\n--- Top 10 prescribers by volume ---")
    top10 = prescriber.nlargest(10, "prescriber_total_encounters")[[
        "prescriber_id", "prescriber_total_encounters",
        "prescriber_antibiotic_rate", "prescriber_polypharmacy_rate"
    ]]
    print(top10.to_string(index=False))

    # ------------------------------------------------------------------
    # Merge prescriber metrics to encounter level
    # ------------------------------------------------------------------
    merge_cols = [
        "prescriber_id",
        "prescriber_antibiotic_rate",
        "prescriber_mean_num_antibiotics",
        "prescriber_polypharmacy_rate",
    ]
    df = df.merge(prescriber[merge_cols], on="prescriber_id", how="left")
    print(f"\nMerged prescriber metrics. Dataset: {len(df)} rows, {df.shape[1]} cols")

    # ------------------------------------------------------------------
    # Visualizations
    # ------------------------------------------------------------------
    print("\n--- Creating prescriber visualizations ---")

    # 1. Distribution of prescriber antibiotic rates
    fig, ax = plt.subplots(figsize=(10, 6))
    prescriber["prescriber_antibiotic_rate"].plot(
        kind="hist", bins=20, ax=ax, color="salmon", edgecolor="black"
    )
    ax.set_title("Distribution of Prescriber Antibiotic Rates", fontsize=14)
    ax.set_xlabel("Antibiotic Prescribing Rate")
    ax.set_ylabel("Number of Prescribers")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/06_prescriber_ab_rate_dist.png", dpi=150)
    plt.close()

    # 2. Prescriber volume vs antibiotic rate scatter
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(
        prescriber["prescriber_total_encounters"],
        prescriber["prescriber_antibiotic_rate"],
        alpha=0.5, edgecolors="black", linewidth=0.5
    )
    ax.set_title("Prescriber Volume vs Antibiotic Rate", fontsize=14)
    ax.set_xlabel("Total Encounters")
    ax.set_ylabel("Antibiotic Rate")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/07_prescriber_volume_vs_ab.png", dpi=150)
    plt.close()

    # 3. Box plot of prescriber rates
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, col, title in zip(axes, [
        "prescriber_antibiotic_rate",
        "prescriber_mean_num_antibiotics",
        "prescriber_polypharmacy_rate"
    ], [
        "Antibiotic Rate",
        "Mean # Antibiotics",
        "Polypharmacy Rate"
    ]):
        sns.boxplot(y=prescriber[col], ax=ax)
        ax.set_title(title, fontsize=12)
    plt.suptitle("Prescriber Behaviour Distributions", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/08_prescriber_behaviour_box.png", dpi=150)
    plt.close()

    print(f"  Saved prescriber figures to {FIGURES_DIR}/")

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    df.to_csv(ENCOUNTER_PRESCRIBER_PATH, index=False)
    print(f"\nSaved: {ENCOUNTER_PRESCRIBER_PATH}")
    return df


if __name__ == "__main__":
    run()
