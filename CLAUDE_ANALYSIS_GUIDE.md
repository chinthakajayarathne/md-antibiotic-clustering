# Step-by-Step Guide: Using Claude for Antibiotic Prescribing Clustering Analysis

## Overview
This guide contains exact prompts to use with Claude at each stage of your analysis. You'll upload your data and copy-paste these prompts to get Claude to do the work.

---

## STEP 1: Data Preparation & Exploration

### What You Need:
- Your extracted CSV file with raw data (one row per drug per encounter)

### Prompt to Use:

```
I have extracted outpatient prescription data from HHIMS for January 2026. The data is in CSV format with one row per drug per encounter. 

Please help me:

1. Load the data and show me basic statistics (number of rows, columns, date range)

2. Transform it to encounter-level format where:
   - One row = one encounter (OPDID)
   - Aggregate all drugs prescribed in that encounter
   - Create these derived variables:
     * age_months = months between DateOfBirth and DateTimeOfVisit
     * age_stratum (as per the categories in my spec)
     * num_prescription_items = total drugs prescribed
     * num_distinct_drugs = unique drugs
     * has_antibiotic (1 if drug_group contains 'Antibiotics')
     * num_antibiotics = count of antibiotic drugs
     * antibiotic_monotherapy = 1 if num_antibiotics == 1
     * antibiotic_combination = 1 if num_antibiotics >= 2
     * polypharmacy_flag = 1 if num_distinct_drugs >= 3

3. Clean the data:
   - Remove encounters where age_months < 0 or > 216
   - Remove PatientWeight < 0 or > 150 kg
   - Keep weight as NaN if missing

4. Show me exploratory statistics:
   - Total encounters
   - Overall antibiotic prescribing rate
   - Antibiotic rate by age_stratum
   - Distribution of num_distinct_drugs
   - Polypharmacy rate

5. Create visualizations:
   - Bar chart of encounters by age group
   - Pie chart of antibiotic vs non-antibiotic encounters
   - Histogram of number of drugs per encounter
   - Box plot of antibiotics by age stratum

6. Save the cleaned encounter-level dataset as 'encounter_level_clean.csv'

I'm a beginner to coding, so please explain each step simply and show me the code.
```

### Upload Your File:
- Drag and drop your raw CSV file when Claude asks for it

---

## STEP 2: Prescriber Behavior Analysis

### What You Need:
- The cleaned encounter-level CSV from Step 1

### Prompt to Use:

```
I have my cleaned encounter-level data. Now I need to calculate prescriber behavior variables.

Please:

1. Calculate for each prescriber (prescriber_id):
   - prescriber_antibiotic_rate = (encounters with antibiotics / total encounters)
   - prescriber_mean_num_antibiotics = average antibiotics per encounter
   - prescriber_polypharmacy_rate = (encounters with 3+ drugs / total encounters)

2. Merge these prescriber variables back to the encounter-level dataset

3. Show me:
   - Summary statistics of prescriber behavior
   - Top 10 prescribers by volume
   - Distribution of prescriber antibiotic rates
   - Box plot comparing prescriber rates

4. Save the enhanced dataset as 'encounter_level_with_prescriber.csv'

Keep explanations simple for a beginner.
```

---

## STEP 3: Clustering Analysis

### What You Need:
- The encounter-level data with prescriber variables from Step 2

### Prompt to Use:

```
I'm ready to perform clustering analysis to identify antibiotic prescribing archetypes.

My specifications require:
- Use k-medoids clustering with Gower distance (for mixed data types)
- Test k = 3 to 8 clusters
- Evaluate using silhouette scores
- Use bootstrap resampling for validation

Features to include:
- Numerical (scaled): age_months, PatientWeight, num_distinct_drugs, num_antibiotics, prescriber_antibiotic_rate
- Binary: has_antibiotic, antibiotic_combination, polypharmacy_flag
- Categorical (one-hot encoded): age_stratum, Gender, VisitType

Please:

1. Prepare the feature matrix with proper scaling and encoding

2. Calculate Gower distance matrix

3. Run k-medoids for k=3 to 8 and calculate silhouette scores for each

4. Show me a plot of silhouette scores to help choose optimal k

5. Once I confirm the best k, run the final clustering and show me:
   - Cluster sizes
   - Cluster profiles (mean values for each feature)
   - Cross-tabulation of clusters with age_stratum
   - Antibiotic rate per cluster

6. Create visualizations:
   - PCA plot showing clusters in 2D space
   - Heatmap of cluster characteristics
   - Bar charts comparing clusters on key metrics

7. Save the dataset with cluster assignments as 'encounter_level_clustered.csv'

I'm a beginner, so explain the clustering results in clinical terms.
```

---

## STEP 4: Cluster Interpretation & Archetype Naming

### What You Need:
- The clustered dataset from Step 3

### Prompt to Use:

```
Now I need to interpret my clusters and name them as prescribing archetypes.

For each cluster, please analyze and summarize:

1. Clinical profile:
   - Dominant age groups
   - Average patient weight
   - Common visit types

2. Prescribing pattern:
   - Antibiotic use rate
   - Mono vs combination therapy
   - Polypharmacy prevalence
   - Average number of drugs

3. Prescriber characteristics:
   - Typical prescriber antibiotic rate
   - Prescriber variation within cluster

4. Top 10 most common complaints in this cluster

5. Top 10 most frequently prescribed drugs

Based on these profiles, suggest clinically meaningful archetype names for each cluster (e.g., "Conservative prescribers", "High antibiotic users", "Guideline-concordant", etc.)

Create a comprehensive summary report as a Word document with:
- Executive summary table comparing all clusters
- Detailed profile for each cluster
- Visualizations embedded
- Clinical interpretation

I'm writing this for my MD thesis, so make it professional but clear.
```

---

## STEP 5: Validation Analysis

### What You Need:
- The clustered dataset

### Prompt to Use:

```
I need to validate my clustering using bootstrap resampling as specified in my research proposal.

Please:

1. Perform bootstrap validation:
   - Run clustering 100 times on random samples (80% of data)
   - Calculate stability metrics (how often same encounters cluster together)
   - Report cluster stability scores

2. Create a stability heatmap showing cluster consistency

3. Check if clusters are clinically distinct:
   - Run statistical tests comparing clusters on key variables
   - Report p-values for differences

4. Generate a validation summary report documenting:
   - Bootstrap stability results
   - Statistical significance of cluster differences
   - Limitations and interpretation guidance

Save all results and create a summary document for my thesis.

Explain the validation results simply.
```

---

## STEP 6: Create Final Deliverables

### Prompt to Use:

```
I need final deliverables for my MD thesis. Please create:

1. A comprehensive Excel workbook with multiple sheets:
   - Sheet 1: Cluster summary statistics
   - Sheet 2: Full encounter-level data with cluster assignments
   - Sheet 3: Prescriber analysis by cluster
   - Sheet 4: Top drugs per cluster
   - Sheet 5: Validation results

2. A PowerPoint presentation with:
   - Study overview slide
   - Data description (sample size, date range)
   - Key exploratory findings
   - Clustering methodology
   - Cluster profiles (one slide per cluster with visuals)
   - Archetype interpretation
   - Validation results
   - Clinical implications

3. A summary report document covering:
   - Methods used
   - Descriptive statistics
   - Cluster characteristics
   - Archetype descriptions
   - Tables and figures
   - Discussion of clinical relevance

Make everything professional and thesis-ready.
```

---

## TIPS FOR WORKING WITH CLAUDE:

### ✅ DO:
- Upload your data file when asked
- Specify you're a beginner when asking for help
- Ask Claude to explain anything you don't understand
- Request modifications if output doesn't look right
- Save intermediate files at each step

### ❌ DON'T:
- Try to do all steps in one conversation (break it up)
- Upload data with real patient names (use pseudonymized data only)
- Skip the exploratory analysis step
- Ignore warnings or errors - ask Claude to fix them

---

## TROUBLESHOOTING:

**If you get an error:**
```
I got this error: [paste error message]
Please help me fix it and explain what went wrong simply.
```

**If results don't look right:**
```
These results seem unusual because [explain what's wrong].
Can you check the code and recalculate?
```

**If you need to modify something:**
```
Can you change [specific thing] to [what you want] and rerun the analysis?
```

---

## FILE NAMING CONVENTION:

Claude will create these files:
- `encounter_level_clean.csv` - After Step 1
- `encounter_level_with_prescriber.csv` - After Step 2  
- `encounter_level_clustered.csv` - After Step 3
- `cluster_analysis_report.docx` - After Step 4
- `validation_results.xlsx` - After Step 5
- `final_presentation.pptx` - After Step 6

---

## ESTIMATED TIME:

- Step 1: 10-15 minutes
- Step 2: 5-10 minutes
- Step 3: 15-20 minutes (longest step)
- Step 4: 10-15 minutes
- Step 5: 10-15 minutes
- Step 6: 10-15 minutes

**Total: About 1-1.5 hours** (excluding time for you to review and understand results)

---

## NEXT STEPS AFTER CLUSTERING:

This analysis gives you Phase 2 outputs for your thesis:
✅ Identified prescribing clusters
✅ Characterized prescribing archetypes
✅ Quantified patterns

You'll use these clusters in Phase 3 for:
- Designing your TDF questionnaire
- Creating vignettes for qualitative interviews
- Guiding expert review discussions

Good luck with your research!
