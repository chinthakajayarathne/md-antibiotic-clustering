# QUICK REFERENCE: Copy-Paste Prompts for Claude

Use these condensed prompts when working with Claude. Just copy-paste and upload your data.

---

## 📊 STEP 1: Data Prep & EDA
**Upload:** Raw CSV file  
**Copy this:**

```
I have HHIMS outpatient data (one row per drug per encounter) for January 2026. 

Transform to encounter-level (one row per OPDID) and create: age_months, age_stratum, num_prescription_items, num_distinct_drugs, has_antibiotic, num_antibiotics, antibiotic_monotherapy, antibiotic_combination, polypharmacy_flag.

Clean: Remove age_months <0 or >216, remove weight <0 or >150kg.

Show: total encounters, antibiotic rate, antibiotic rate by age_stratum, polypharmacy rate.

Visualize: age distribution, antibiotic vs non-antibiotic pie chart, drugs per encounter histogram, antibiotics by age box plot.

Save as 'encounter_level_clean.csv'. I'm a beginner - keep it simple!
```

---

## 👨‍⚕️ STEP 2: Prescriber Analysis
**Upload:** encounter_level_clean.csv  
**Copy this:**

```
Calculate per prescriber: prescriber_antibiotic_rate, prescriber_mean_num_antibiotics, prescriber_polypharmacy_rate. 

Merge back to encounters. Show summary stats and top 10 prescribers. 

Save as 'encounter_level_with_prescriber.csv'. Simple explanations please!
```

---

## 🎯 STEP 3: Clustering
**Upload:** encounter_level_with_prescriber.csv  
**Copy this:**

```
Run k-medoids clustering with Gower distance for k=3 to 8.

Features: age_months, PatientWeight, num_distinct_drugs, num_antibiotics, prescriber_antibiotic_rate (scaled), has_antibiotic, antibiotic_combination, polypharmacy_flag (binary), age_stratum, Gender, VisitType (one-hot).

Show silhouette scores plot. After I pick k, show cluster profiles, PCA plot, heatmap, and cluster comparisons.

Save as 'encounter_level_clustered.csv'. Beginner-friendly please!
```

---

## 🏷️ STEP 4: Archetype Naming
**Upload:** encounter_level_clustered.csv  
**Copy this:**

```
For each cluster, analyze: clinical profile, prescribing pattern, prescriber characteristics, top complaints, top drugs.

Suggest archetype names (e.g., "Conservative", "High antibiotic use").

Create professional Word report with summary table, detailed profiles, visualizations. Thesis-ready format.
```

---

## ✅ STEP 5: Validation
**Upload:** encounter_level_clustered.csv  
**Copy this:**

```
Bootstrap validation: 100 iterations, 80% samples. Calculate stability metrics and create heatmap.

Run statistical tests comparing clusters. Generate validation summary report.

Simple explanations please!
```

---

## 📦 STEP 6: Deliverables
**Upload:** All previous files  
**Copy this:**

```
Create: 
1. Excel workbook (cluster stats, full data, prescriber analysis, top drugs, validation)
2. PowerPoint (overview, methods, cluster profiles, validation, implications)
3. Summary report document (methods, results, tables, figures)

Make thesis-ready and professional.
```

---

## 🆘 TROUBLESHOOTING PROMPTS

**Error fix:**
```
I got this error: [paste error]. Fix it and explain simply what went wrong.
```

**Unexpected results:**
```
These results look unusual: [explain issue]. Please check and recalculate.
```

**Need changes:**
```
Change [specific thing] to [what you want] and rerun.
```

---

## ⚡ SUPER QUICK VERSION (All in One)

If you want everything at once:

```
I have HHIMS encounter data. Please:
1. Transform to encounter-level with derived variables (antibiotics, polypharmacy)
2. Add prescriber behavior metrics
3. Run k-medoids clustering (k=3-8, Gower distance) 
4. Help me pick optimal k based on silhouette scores
5. Create cluster profiles and archetype names
6. Validate with bootstrap
7. Generate Excel, PowerPoint, and Word deliverables

I'm a beginner - keep explanations simple! Data uploaded.
```

---

**Remember:** 
- One step at a time works best
- Always save intermediate files
- Ask Claude to explain anything unclear
- You can pause and resume anytime

