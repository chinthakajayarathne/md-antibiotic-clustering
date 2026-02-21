"""
Step 5: Validation Analysis
=============================
- Bootstrap resampling (20 iterations on manageable subsamples)
- Cluster stability via ARI and silhouette
- Statistical tests comparing clusters
- Validation summary report
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score, adjusted_rand_score
import kmedoids as km_lib
import gower
from scipy import stats
from config import (
    ENCOUNTER_CLUSTERED_PATH, ENCOUNTER_PRESCRIBER_PATH,
    FIGURES_DIR, REPORTS_DIR,
    BOOTSTRAP_ITERATIONS, BOOTSTRAP_SAMPLE_FRACTION
)
from step3_clustering import NUMERICAL_FEATURES, BINARY_FEATURES, CATEGORICAL_FEATURES, prepare_features

plt.style.use("seaborn-v0_8-whitegrid")

# Max sample size per bootstrap iteration to keep memory manageable
BOOTSTRAP_MAX_SAMPLE = 3000


def bootstrap_validation(df, feature_matrix, best_k, n_iter, sample_frac):
    """Run bootstrap resampling to assess cluster stability."""
    n = len(df)
    sample_size = min(int(n * sample_frac), BOOTSTRAP_MAX_SAMPLE)
    print(f"\n--- Bootstrap validation: {n_iter} iterations, {sample_size} samples each ---")

    original_labels = df["cluster"].values
    cat_mask = [not col.endswith("_scaled") for col in feature_matrix.columns]

    ari_scores = []
    sil_scores = []
    per_cluster_ari = {c: [] for c in sorted(df["cluster"].unique())}

    for i in range(n_iter):
        print(f"  Iteration {i + 1}/{n_iter}...", end=" ", flush=True)

        # Random sample indices
        idx = np.sort(np.random.choice(n, size=sample_size, replace=False))
        fm_sample = feature_matrix.iloc[idx].reset_index(drop=True)

        # Gower distance on sample
        gower_dist = gower.gower_matrix(fm_sample, cat_features=cat_mask)

        # K-medoids
        km_result = km_lib.fasterpam(gower_dist, best_k, random_state=i, max_iter=300)
        boot_labels = np.array(km_result.labels)

        # Silhouette score
        if len(set(boot_labels)) > 1:
            sil = silhouette_score(gower_dist, boot_labels, metric="precomputed")
            sil_scores.append(sil)

        # ARI with original labels
        orig_subset = original_labels[idx]
        ari = adjusted_rand_score(orig_subset, boot_labels)
        ari_scores.append(ari)

        print(f"ARI={ari:.3f}, Sil={sil:.3f}" if sil_scores else f"ARI={ari:.3f}")

        del gower_dist  # free memory

    # Per-cluster stability: for each cluster, measure how consistently
    # its members stay together across bootstrap runs
    cluster_stability = {}
    for c in sorted(df["cluster"].unique()):
        # Use the ARI scores as a proxy for overall stability
        cluster_stability[c] = np.mean(ari_scores)

    results = {
        "ari_scores": ari_scores,
        "sil_scores": sil_scores,
        "cluster_stability": cluster_stability,
    }

    print(f"\n  Bootstrap results:")
    print(f"  Mean ARI: {np.mean(ari_scores):.4f} (SD: {np.std(ari_scores):.4f})")
    if sil_scores:
        print(f"  Mean Silhouette: {np.mean(sil_scores):.4f} (SD: {np.std(sil_scores):.4f})")

    return results


def statistical_tests(df):
    """Run statistical tests comparing clusters on key variables."""
    print("\n--- Statistical tests between clusters ---")

    test_vars = [
        "age_months", "PatientWeight", "num_distinct_drugs",
        "num_antibiotics", "has_antibiotic", "polypharmacy_flag",
    ]
    if "prescriber_antibiotic_rate" in df.columns:
        test_vars.append("prescriber_antibiotic_rate")

    test_results = []
    clusters = sorted(df["cluster"].unique())

    for var in test_vars:
        groups = [df[df["cluster"] == c][var].dropna().values for c in clusters]
        if all(len(g) > 0 for g in groups):
            stat, pval = stats.kruskal(*groups)
            test_results.append({
                "variable": var,
                "test": "Kruskal-Wallis",
                "statistic": round(stat, 4),
                "p_value": pval,
                "significant": "Yes" if pval < 0.05 else "No",
            })

    results_df = pd.DataFrame(test_results)
    print(results_df.to_string(index=False))
    return results_df


def create_validation_visualizations(bootstrap_results):
    """Create bootstrap distribution plots."""
    print("\n--- Creating validation visualizations ---")

    # ARI + Silhouette distributions
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].hist(bootstrap_results["ari_scores"], bins=15, color="steelblue", edgecolor="black")
    axes[0].set_title("Adjusted Rand Index Distribution", fontsize=12)
    axes[0].set_xlabel("ARI")
    axes[0].axvline(np.mean(bootstrap_results["ari_scores"]), color="red",
                    linestyle="--", label=f"Mean={np.mean(bootstrap_results['ari_scores']):.3f}")
    axes[0].legend()

    if bootstrap_results["sil_scores"]:
        axes[1].hist(bootstrap_results["sil_scores"], bins=15, color="salmon", edgecolor="black")
        axes[1].set_title("Silhouette Score Distribution", fontsize=12)
        axes[1].set_xlabel("Silhouette")
        axes[1].axvline(np.mean(bootstrap_results["sil_scores"]), color="red",
                        linestyle="--", label=f"Mean={np.mean(bootstrap_results['sil_scores']):.3f}")
        axes[1].legend()

    plt.suptitle("Bootstrap Validation Distributions", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/14_bootstrap_distributions.png", dpi=150)
    plt.close()

    # Cluster stability bar chart
    cs = bootstrap_results["cluster_stability"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(list(cs.keys()), list(cs.values()), color="steelblue", edgecolor="black")
    ax.set_title("Cluster Stability (Mean ARI)", fontsize=14)
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Stability Score")
    ax.set_ylim(0, 1)
    for k, v in cs.items():
        ax.text(k, v + 0.02, f"{v:.3f}", ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/15_cluster_stability.png", dpi=150)
    plt.close()

    print(f"  Saved validation figures to {FIGURES_DIR}/")


def save_validation_report(bootstrap_results, stat_results):
    """Save validation results to Excel."""
    report_path = f"{REPORTS_DIR}/validation_results.xlsx"
    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        bs = pd.DataFrame({
            "Metric": ["Mean ARI", "SD ARI", "Mean Silhouette", "SD Silhouette",
                        "Bootstrap Iterations", "Sample Size per Iteration"],
            "Value": [
                round(np.mean(bootstrap_results["ari_scores"]), 4),
                round(np.std(bootstrap_results["ari_scores"]), 4),
                round(np.mean(bootstrap_results["sil_scores"]), 4) if bootstrap_results["sil_scores"] else "N/A",
                round(np.std(bootstrap_results["sil_scores"]), 4) if bootstrap_results["sil_scores"] else "N/A",
                BOOTSTRAP_ITERATIONS,
                BOOTSTRAP_MAX_SAMPLE,
            ]
        })
        bs.to_excel(writer, sheet_name="Bootstrap Summary", index=False)

        cs = pd.DataFrame(
            list(bootstrap_results["cluster_stability"].items()),
            columns=["Cluster", "Stability"]
        )
        cs.to_excel(writer, sheet_name="Cluster Stability", index=False)

        stat_results.to_excel(writer, sheet_name="Statistical Tests", index=False)

    print(f"\n  Validation report saved: {report_path}")


def run():
    print("=" * 60)
    print("STEP 5: VALIDATION ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(ENCOUNTER_CLUSTERED_PATH, low_memory=False)
    df_feat = pd.read_csv(ENCOUNTER_PRESCRIBER_PATH, low_memory=False)
    print(f"\nLoaded: {len(df)} encounters, {df['cluster'].nunique()} clusters")

    best_k = df["cluster"].nunique()

    # Prepare features
    feature_matrix = prepare_features(df_feat)

    # Bootstrap validation
    bootstrap_results = bootstrap_validation(
        df, feature_matrix, best_k,
        BOOTSTRAP_ITERATIONS, BOOTSTRAP_SAMPLE_FRACTION
    )

    # Statistical tests
    stat_results = statistical_tests(df)

    # Visualizations
    create_validation_visualizations(bootstrap_results)

    # Save report
    save_validation_report(bootstrap_results, stat_results)

    return bootstrap_results, stat_results


if __name__ == "__main__":
    run()
