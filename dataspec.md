# Encounter-Level Antibiotic Stewardship Analysis

## Data Extraction and Analysis Specification

------------------------------------------------------------------------

## 1. Objective

To construct an encounter-level dataset from EMR data for modelling
paediatric outpatient prescribing patterns and identifying antibiotic
prescribing archetypes.

**Unit of analysis:** One row per OPD encounter (OPDID).

**Initial time window:**\
2026-01-01 ≤ DateTimeOfVisit \< 2026-02-01

------------------------------------------------------------------------

## 2. Data Sources

The dataset is constructed from the following EMR tables:

-   opd_visits (ov)
-   patient (p)
-   opd_presciption (op)
-   prescribe_items (pit)
-   who_drug (whod)

------------------------------------------------------------------------

## 3. Join Structure

``` sql
opd_visits (ov)
    JOIN patient (p) ON ov.PID = p.PID
    JOIN opd_presciption (op) ON ov.OPDID = op.OPDID
    JOIN prescribe_items (pit) ON pit.PRES_ID = op.PRSID
    JOIN who_drug (whod) ON pit.DRGID = whod.wd_id
```

------------------------------------------------------------------------

## 4. Extracted Fields

### Encounter-Level Fields

-   OPDID
-   DateTimeOfVisit
-   OnSetDate
-   Complaint
-   VisitType
-   PatientWeight

### Patient-Level Fields

-   PID (for linkage only)
-   DateOfBirth (used only for age calculation)
-   Gender

### Prescription-Level Fields

-   DRGID
-   Dosage
-   HowLong
-   Quantity
-   Frequency
-   DoseComment

### Drug Reference Fields

-   whod.name
-   whod.group
-   whod.sub_group

### Prescriber

-   Doctor (prescriber_id)

------------------------------------------------------------------------

## 5. Derived Variables

### 5.1 Age Variables

-   age_months = TIMESTAMPDIFF(MONTH, DateOfBirth, DateTimeOfVisit)

Age strata:

  Condition     Stratum
  ------------- -------------------
  0--27 days    neonate_0\_27d
  \<3 months    infant_1\_2m
  \<6 months    infant_3\_5m
  \<12 months   infant_6\_11m
  \<24 months   toddler_12_23m
  \<5 years     preschool_2\_4y
  \<12 years    child_5\_11y
  \<18 years    adolescent_12_17y
  else          adult_18plus

DateOfBirth must NOT be retained in the final modelling dataset.

------------------------------------------------------------------------

### 5.2 Encounter-Level Aggregations (Grouped by OPDID)

-   num_prescription_items = COUNT(\*)
-   num_distinct_drugs = COUNT(DISTINCT DRGID)

### Antibiotic Indicators

Based on:

whod.group = 'Antibiotics'

Derived variables:

-   has_antibiotic = 1 if at least one antibiotic exists in encounter
-   num_antibiotics = count of antibiotic drugs
-   antibiotic_monotherapy = num_antibiotics == 1
-   antibiotic_combination = num_antibiotics \>= 2
-   polypharmacy_flag = num_distinct_drugs \>= 3

------------------------------------------------------------------------

## 6. Data Cleaning Rules

### Weight

-   Remove negative values
-   Remove weight \> 150 kg
-   Retain missing values as NaN

### Age

-   Remove encounters where age_months \< 0
-   Remove encounters where age_months \> 216

### Drug Groups

-   Trim whitespace
-   Standardize case
-   Ensure consistent label for 'Antibiotics'

------------------------------------------------------------------------

## 7. Feature Engineering for Clustering

### Numerical Features

-   age_months (scaled)
-   PatientWeight (scaled)
-   num_distinct_drugs
-   num_antibiotics
-   prescriber_antibiotic_rate

### Binary Features

-   has_antibiotic
-   antibiotic_combination
-   polypharmacy_flag

### Categorical Features

-   age_stratum (one-hot encoded)
-   Gender (binary or one-hot)
-   VisitType (one-hot encoded)
-   Major drug groups (top N one-hot encoded)

------------------------------------------------------------------------

## 8. Prescriber Behaviour Variables

Compute across the full study window:

-   prescriber_antibiotic_rate = (total encounters with antibiotics) /
    (total encounters)
-   prescriber_mean_num_antibiotics
-   prescriber_polypharmacy_rate

Merge these back to encounter-level dataset.

------------------------------------------------------------------------

## 9. Exploratory Analysis Plan

1.  Total encounters
2.  Antibiotic rate
3.  Distribution of num_antibiotics
4.  Antibiotic rate by age_stratum
5.  Antibiotic rate by prescriber
6.  Polypharmacy rate

------------------------------------------------------------------------

## 10. Clustering Strategy

1.  Standardize numerical features
2.  Perform PCA for structure visualization
3.  Run K-Means with k = 3 to 8
4.  Evaluate silhouette score
5.  Interpret cluster clinical meaning

Optional:

-   Hierarchical clustering (Ward linkage)
-   Stability testing via bootstrapping

------------------------------------------------------------------------

## 11. Expected Outputs

-   Clean encounter-level modelling dataset
-   Distribution summaries
-   Cluster assignments
-   Cluster profiles
-   Prescriber behaviour analysis
-   Antibiotic stewardship archetype interpretation

------------------------------------------------------------------------

End of Specification
