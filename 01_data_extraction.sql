-- ================================================================================
-- HHIMS Data Extraction Query for Antibiotic Stewardship Clustering Analysis
-- ================================================================================
-- Purpose: Extract encounter-level data for January 2026
-- Date Range: 2026-01-01 to 2026-02-01
-- Unit of Analysis: One row per OPD encounter (OPDID)
-- ================================================================================

SELECT 
    -- Encounter identifiers
    ov.OPDID,
    ov.DateTimeOfVisit,
    ov.OnSetDate,
    ov.Complaint,
    ov.VisitType,
    ov.PatientWeight,
    
    -- Patient demographics (PID for pseudonymization, DOB for age calculation only)
    SHA2(CONCAT(ov.PID, 'YOUR_SALT_HERE'), 256) AS patient_id,  -- Pseudonymized
    p.DateOfBirth,
    p.Gender,
    
    -- Prescriber (pseudonymized)
    SHA2(CONCAT(op.Doctor, 'YOUR_SALT_HERE'), 256) AS prescriber_id,
    
    -- Prescription details
    pit.DRGID,
    pit.Dosage,
    pit.HowLong,
    pit.Quantity,
    pit.Frequency,
    pit.DoseComment,
    
    -- Drug reference information
    whod.name AS drug_name,
    whod.group AS drug_group,
    whod.sub_group AS drug_sub_group

FROM opd_visits ov

-- Join patient table
INNER JOIN patient p 
    ON ov.PID = p.PID

-- Join prescription table
INNER JOIN opd_presciption op 
    ON ov.OPDID = op.OPDID

-- Join prescription items
INNER JOIN prescribe_items pit 
    ON pit.PRES_ID = op.PRSID

-- Join drug reference table
INNER JOIN who_drug whod 
    ON pit.DRGID = whod.wd_id

WHERE 
    -- Time window: January 2026
    ov.DateTimeOfVisit >= '2026-01-01 00:00:00'
    AND ov.DateTimeOfVisit < '2026-02-01 00:00:00'
    
    -- Basic data quality filters
    AND ov.OPDID IS NOT NULL
    AND pit.DRGID IS NOT NULL

ORDER BY 
    ov.OPDID, 
    pit.DRGID;

-- ================================================================================
-- NOTES:
-- 1. Replace 'YOUR_SALT_HERE' with a secure salt string for pseudonymization
-- 2. This query returns one row per drug per encounter
-- 3. You'll need to aggregate to encounter level in Python
-- 4. Export results as CSV for analysis
-- ================================================================================
