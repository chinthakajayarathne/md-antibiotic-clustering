"""
Step 3: Clustering Analysis
=============================
- Prepare feature matrix (numerical scaled, binary, categorical one-hot)
- Compute Gower distance matrix
- Run k-medoids for k = 3..8
- Evaluate silhouette scores
- User picks optimal k, then generate cluster profiles
- PCA plot, heatmap, comparisons
- Save encounter_level_clustered.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import gower
from sklearn_extra.cluster import KMedoids
from config import (
    ENCOUNTER_PRESCRIBER_PATH, ENCOUNTER_CLUSTERED_PATH,
    FIGURES_DIR, K_RANGE, AGE_STRATA
)

plt.style.use("seaborn-v0_8-whitegrid")

# Feature definitions
NUMERICAL_FEATURES = [
    "age_months", "PatientWeight", "num_distinct_drugs",
    "num_antibiotics", "prescriber_antibiotic_rate"
]
BINARY_FEATURES = [
    "has_antibiotic", "antibiotic_combination", "polypharmacy_flag"
]
CATEGORICAL_FEATURES = ["age_stratum", "Gender", "VisitType"]


def prepare_features(df):
    """Build the feature matrix for clustering."""
    print("\n--- Preparing feature matrix ---")

    # Handle missing weight: fill with median
    df["PatientWeight"] = df["PatientWeight"].fillna(df["PatientWeight"].median())

    # Scale numerical features
    scaler = StandardScaler()
    num_scaled = pd.DataFrame(
        scaler.fit_transform(df[NUMERICAL_FEATURES]),
        columns=[f"{c}_scaled" for c in NUMERICAL_FEATURES],
        index=df.index,
    )

    # Binary features (already 0/1)
    bin_df = df[BINARY_FEATURES].copy()

    # One-hot encode categorical features
    cat_df = pd.get_dummies(df[CATEGORICAL_FEATURES], drop_first=False).astype(int)

    # Combine
    feature_matrix = pd.concat([num_scaled, bin_df, cat_df], axis=1)
    print(f"  Feature matrix: {feature_matrix.shape[0]} rows x {feature_matrix.shape[1]} features")
    print(f"  Numerical (scaled): {len(NUMERICAL_FEATURES)}")
    print(f"  Binary: {len(BINARY_FEATURES)}")
    print(f"  Categorical one-hot: {cat_df.shape[1]}")

    return feature_matrix


def compute_gower_and_cluster(feature_matrix, k_range):
    """Compute Gower distance and run k-medoids for each k."""
    print("\n--- Computing Gower distance matrix ---")
    # Mark which columns are categorical (binary + one-hot)
    cat_mask = [not col.endswith("_scaled") for col in feature_matrix.columns]
    gower_dist = gower.gower_matrix(feature_matrix, cat_features=cat_mask)
    print(f"  Gower distance matrix: {gower_dist.shape}")

    results = {}
    print("\n--- Running k-medoids for k = {min(k_range)}..{max(k_range)} ---")
    for k in k_range:
        kmed = KMedoids(
            n_clusters=k, metric="precomputed",
            init="k-medoids++", random_state=42, max_iter=300
        )
        labels = kmed.fit_predict(gower_dist)
        sil = silhouette_score(gower_dist, labels, metric="precomputed")
        results[k] = {"labels": labels, "silhouette": sil, "model": kmed}
        print(f"  k={k}: silhouette = {sil:.4f}")

    return gower_dist, results


def plot_silhouette_scores(results):
    """Plot silhouette scores for each k."""
    ks = sorted(results.keys())
    sils = [results[k]["silhouette"] for k in ks]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ks, sils, "o-", color="steelblue", markersize=8, linewidth=2)
    ax.set_title("Silhouette Score by Number of Clusters", fontsize=14)
    ax.set_xlabel("k (Number of Clusters)")
    ax.set_ylabel("Silhouette Score")
    ax.set_xticks(ks)
    for k, s in zip(ks, sils):
        ax.annotate(f"{s:.3f}", (k, s), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/09_silhouette_scores.png", dpi=150)
    plt.close()
    print(f"  Silhouette plot saved.")

    best_k = ks[np.argmax(sils)]
    print(f"\n  ** Best silhouette at k={best_k} ({max(sils):.4f}) **")
    return best_k


def apply_best_k(df, gower_dist, results, best_k):
    """Apply the chosen k and add cluster labels to the dataset."""
    print(f"\n--- Applying k={best_k} clustering ---")
    labels = results[best_k]["labels"]
    df["cluster"] = labels

    print("\nCluster sizes:")
    print(df["cluster"].value_counts().sort_index().to_string())

    return df


def cluster_profiles(df):
    """Print and return cluster profile summaries."""
    print("\n--- Cluster Profiles ---")

    profile_cols = [
        "age_months", "PatientWeight", "num_distinct_drugs",
        "num_antibiotics", "has_antibiotic",
        "antibiotic_monotherapy", "antibiotic_combination",
        "polypharmacy_flag", "prescriber_antibiotic_rate",
    ]

    profiles = df.groupby("cluster")[profile_cols].mean().round(3)
    print(profiles.to_string())

    # Antibiotic rate per cluster
    print("\nAntibiotic rate per cluster:")
    ab_rate = df.groupby("cluster")["has_antibiotic"].mean() * 100
    for c, r in ab_rate.items():
        print(f"  Cluster {c}: {r:.1f}%")

    # Cross-tab: cluster x age_stratum
    print("\nCluster x Age Stratum cross-tabulation:")
    ct = pd.crosstab(df["cluster"], df["age_stratum"])
    print(ct.to_string())

    return profiles


def create_cluster_visualizations(df, feature_matrix, profiles):
    """PCA plot, heatmap, bar comparisons."""
    print("\n--- Creating cluster visualizations ---")

    # 1. PCA 2D plot
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(feature_matrix)
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(coords[:, 0], coords[:, 1], c=df["cluster"],
                         cmap="tab10", alpha=0.5, s=10)
    ax.set_title("PCA Projection of Clusters", fontsize=14)
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    plt.colorbar(scatter, label="Cluster")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/10_pca_clusters.png", dpi=150)
    plt.close()

    # 2. Heatmap of cluster characteristics
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(profiles.T, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax)
    ax.set_title("Cluster Characteristic Heatmap", fontsize=14)
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Feature")
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/11_cluster_heatmap.png", dpi=150)
    plt.close()

    # 3. Bar chart comparing key metrics across clusters
    key_metrics = ["has_antibiotic", "polypharmacy_flag", "antibiotic_combination"]
    cluster_means = df.groupby("cluster")[key_metrics].mean() * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    cluster_means.plot(kind="bar", ax=ax, edgecolor="black")
    ax.set_title("Key Metrics by Cluster (%)", fontsize=14)
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Percentage")
    ax.legend(title="Metric")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/12_cluster_comparison_bars.png", dpi=150)
    plt.close()

    # 4. Cluster size bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    df["cluster"].value_counts().sort_index().plot(
        kind="bar", ax=ax, color="steelblue", edgecolor="black"
    )
    ax.set_title("Cluster Sizes", fontsize=14)
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Number of Encounters")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/13_cluster_sizes.png", dpi=150)
    plt.close()

    print(f"  Saved cluster figures to {FIGURES_DIR}/")


def run():
    print("=" * 60)
    print("STEP 3: CLUSTERING ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(ENCOUNTER_PRESCRIBER_PATH, low_memory=False)
    print(f"\nLoaded: {len(df)} encounters")

    # Prepare features
    feature_matrix = prepare_features(df)

    # Gower + k-medoids
    gower_dist, results = compute_gower_and_cluster(feature_matrix, K_RANGE)

    # Silhouette plot & best k
    best_k = plot_silhouette_scores(results)

    # Apply best k
    df = apply_best_k(df, gower_dist, results, best_k)

    # Profiles
    profiles = cluster_profiles(df)

    # Visualizations
    create_cluster_visualizations(df, feature_matrix, profiles)

    # Save
    df.to_csv(ENCOUNTER_CLUSTERED_PATH, index=False)
    print(f"\nSaved: {ENCOUNTER_CLUSTERED_PATH}")
    print(f"\nNote: If you want a different k, edit K_BEST in config or re-run with a modified script.")

    return df, gower_dist, results, best_k


if __name__ == "__main__":
    run()
