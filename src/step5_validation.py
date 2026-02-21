"""
Step 5: Validation Analysis
=============================
- Bootstrap resampling (100 iterations, 80% sample)
- Cluster stability metrics
- Statistical tests comparing clusters
- Stability heatmap
- Validation summary report
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn_extra.cluster import KMedoids
import gower
from scipy import stats
from config import (
    ENCOUNTER_CLUSTERED_PATH, ENCOUNTER_PRESCRIBER_PATH,
    FIGURES_DIR, REPORTS_DIR,
    BOOTSTRAP_ITERATIONS, BOOTSTRAP_SAMPLE_FRACTION
)
from step3_clustering import NUMERICAL_FEATURES, BINARY_FEATURES, CATEGORICAL_FEATURES, prepare_features

plt.style.use("seaborn-v0_8-whitegrid")


def bootstrap_validation(df, feature_matrix, best_k, n_iter, sample_frac):
    """Run bootstrap resampling to assess cluster stability."""
    print(f"\n--- Bootstrap validation: {n_iter} iterations, {sample_frac*100:.0f}% samples ---")

    n = len(df)
    sample_size = int(n * sample_frac)
    original_labels = df["cluster"].values

    # Co-association matrix: how often pairs cluster together
    coassoc = np.zeros((n, n))
    count_matrix = np.zeros((n, n))
    ari_scores = []
    sil_scores = []

    cat_mask = [not col.endswith("_scaled") for col in feature_matrix.columns]

    for i in range(n_iter):
        if (i + 1) % 10 == 0:
            print(f"  Iteration {i + 1}/{n_iter}")

        # Random sample indices
        idx = np.random.choice(n, size=sample_size, replace=False)
        idx_sorted = np.sort(idx)

        fm_sample = feature_matrix.iloc[idx_sorted].reset_index(drop=True)

        # Gower distance on sample
        gower_dist = gower.gower_matrix(fm_sample, cat_features=cat_mask)

        # K-medoids
        kmed = KMedoids(
            n_clusters=best_k, metric="precomputed",
            init="k-medoids++", random_state=i, max_iter=300
        )
        boot_labels = kmed.fit_predict(gower_dist)

        # Silhouette score
        if len(set(boot_labels)) > 1:
            sil = silhouette_score(gower_dist, boot_labels, metric="precomputed")
            sil_scores.append(sil)

        # ARI with original labels (for the sampled subset)
        orig_subset = original_labels[idx_sorted]
        ari = adjusted_rand_score(orig_subset, boot_labels)
        ari_scores.append(ari)

        # Update co-association matrix
        for a in range(len(idx_sorted)):
            for b in range(a + 1, len(idx_sorted)):
                i_a, i_b = idx_sorted[a], idx_sorted[b]
                count_matrix[i_a, i_b] += 1
                count_matrix[i_b, i_a] += 1
                if boot_labels[a] == boot_labels[b]:
                    coassoc[i_a, i_b] += 1
                    coassoc[i_b, i_a] += 1

    # Normalize co-association
    with np.errstate(divide="ignore", invalid="ignore"):
        stability_matrix = np.where(count_matrix > 0, coassoc / count_matrix, 0)

    # Per-cluster stability: mean co-assoc within cluster
    cluster_stability = {}
    for c in sorted(df["cluster"].unique()):
        members = np.where(original_labels == c)[0]
        if len(members) > 1:
            pairs = stability_matrix[np.ix_(members, members)]
            np.fill_diagonal(pairs, np.nan)
            cluster_stability[c] = np.nanmean(pairs)
        else:
            cluster_stability[c] = 1.0

    results = {
        "ari_scores": ari_scores,
        "sil_scores": sil_scores,
        "stability_matrix": stability_matrix,
        "cluster_stability": cluster_stability,
    }

    print(f"\n  Bootstrap results:")
    print(f"  Mean ARI: {np.mean(ari_scores):.4f} (SD: {np.std(ari_scores):.4f})")
    print(f"  Mean Silhouette: {np.mean(sil_scores):.4f} (SD: {np.std(sil_scores):.4f})")
    print(f"  Cluster stability scores:")
    for c, s in cluster_stability.items():
        print(f"    Cluster {c}: {s:.4f}")

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

        # Kruskal-Wallis (non-parametric)
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


def create_validation_visualizations(bootstrap_results, df):
    """Create stability heatmap and distribution plots."""
    print("\n--- Creating validation visualizations ---")

    # 1. Stability heatmap (sampled for readability if large)
    stability = bootstrap_results["stability_matrix"]
    labels = df["cluster"].values
    order = np.argsort(labels)

    # Sample if too large
    n = len(order)
    if n > 500:
        sample_idx = np.random.choice(n, 500, replace=False)
        sample_idx = np.sort(sample_idx)
    else:
        sample_idx = order

    fig, ax = plt.subplots(figsize=(10, 8))
    sub_matrix = stability[np.ix_(sample_idx, sample_idx)]
    sns.heatmap(sub_matrix, cmap="YlOrRd", vmin=0, vmax=1, ax=ax,
                xticklabels=False, yticklabels=False)
    ax.set_title("Co-Association Stability Heatmap (Bootstrap)", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/14_stability_heatmap.png", dpi=150)
    plt.close()

    # 2. ARI distribution
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].hist(bootstrap_results["ari_scores"], bins=20, color="steelblue", edgecolor="black")
    axes[0].set_title("Adjusted Rand Index Distribution", fontsize=12)
    axes[0].set_xlabel("ARI")
    axes[0].axvline(np.mean(bootstrap_results["ari_scores"]), color="red", linestyle="--", label="Mean")
    axes[0].legend()

    axes[1].hist(bootstrap_results["sil_scores"], bins=20, color="salmon", edgecolor="black")
    axes[1].set_title("Silhouette Score Distribution", fontsize=12)
    axes[1].set_xlabel("Silhouette")
    axes[1].axvline(np.mean(bootstrap_results["sil_scores"]), color="red", linestyle="--", label="Mean")
    axes[1].legend()

    plt.suptitle("Bootstrap Validation Distributions", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/15_bootstrap_distributions.png", dpi=150)
    plt.close()

    # 3. Cluster stability bar chart
    cs = bootstrap_results["cluster_stability"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(cs.keys(), cs.values(), color="steelblue", edgecolor="black")
    ax.set_title("Cluster Stability Scores", fontsize=14)
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Stability (0-1)")
    ax.set_ylim(0, 1)
    for k, v in cs.items():
        ax.text(k, v + 0.02, f"{v:.3f}", ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/16_cluster_stability.png", dpi=150)
    plt.close()

    print(f"  Saved validation figures to {FIGURES_DIR}/")


def save_validation_report(bootstrap_results, stat_results):
    """Save validation results to Excel."""
    report_path = f"{REPORTS_DIR}/validation_results.xlsx"
    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        # Bootstrap summary
        bs = pd.DataFrame({
            "Metric": ["Mean ARI", "SD ARI", "Mean Silhouette", "SD Silhouette"],
            "Value": [
                round(np.mean(bootstrap_results["ari_scores"]), 4),
                round(np.std(bootstrap_results["ari_scores"]), 4),
                round(np.mean(bootstrap_results["sil_scores"]), 4),
                round(np.std(bootstrap_results["sil_scores"]), 4),
            ]
        })
        bs.to_excel(writer, sheet_name="Bootstrap Summary", index=False)

        # Cluster stability
        cs = pd.DataFrame(
            list(bootstrap_results["cluster_stability"].items()),
            columns=["Cluster", "Stability"]
        )
        cs.to_excel(writer, sheet_name="Cluster Stability", index=False)

        # Statistical tests
        stat_results.to_excel(writer, sheet_name="Statistical Tests", index=False)

    print(f"\n  Validation report saved: {report_path}")


def run():
    print("=" * 60)
    print("STEP 5: VALIDATION ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(ENCOUNTER_CLUSTERED_PATH, low_memory=False)
    # Also need encounter_with_prescriber for feature prep
    df_feat = pd.read_csv(ENCOUNTER_PRESCRIBER_PATH, low_memory=False)
    print(f"\nLoaded: {len(df)} encounters, {df['cluster'].nunique()} clusters")

    best_k = df["cluster"].nunique()

    # Prepare features (same as step 3)
    feature_matrix = prepare_features(df_feat)

    # Bootstrap validation
    bootstrap_results = bootstrap_validation(
        df, feature_matrix, best_k,
        BOOTSTRAP_ITERATIONS, BOOTSTRAP_SAMPLE_FRACTION
    )

    # Statistical tests
    stat_results = statistical_tests(df)

    # Visualizations
    create_validation_visualizations(bootstrap_results, df)

    # Save report
    save_validation_report(bootstrap_results, stat_results)

    return bootstrap_results, stat_results


if __name__ == "__main__":
    run()
