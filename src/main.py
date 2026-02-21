"""
Main Pipeline Runner
=====================
Runs all 6 steps of the antibiotic prescribing clustering analysis.

Usage:
    python main.py          # Run all steps
    python main.py 1        # Run only step 1
    python main.py 3 4 5    # Run steps 3, 4, and 5
"""
import sys
import time


def run_step(step_num):
    """Run a single step by number."""
    start = time.time()
    if step_num == 1:
        from step1_data_preparation import run
        run()
    elif step_num == 2:
        from step2_prescriber_analysis import run
        run()
    elif step_num == 3:
        from step3_clustering import run
        run()
    elif step_num == 4:
        from step4_archetype_interpretation import run
        run()
    elif step_num == 5:
        from step5_validation import run
        run()
    elif step_num == 6:
        from step6_deliverables import run
        run()
    else:
        print(f"Unknown step: {step_num}")
        return
    elapsed = time.time() - start
    print(f"\n[Step {step_num} completed in {elapsed:.1f}s]")


def main():
    if len(sys.argv) > 1:
        steps = [int(s) for s in sys.argv[1:]]
    else:
        steps = [1, 2, 3, 4, 5, 6]

    print("=" * 60)
    print("ANTIBIOTIC PRESCRIBING CLUSTERING ANALYSIS PIPELINE")
    print("=" * 60)
    print(f"Steps to run: {steps}\n")

    total_start = time.time()
    for step in steps:
        run_step(step)
        print()

    total_elapsed = time.time() - total_start
    print("=" * 60)
    print(f"PIPELINE COMPLETE ({total_elapsed:.1f}s total)")
    print("=" * 60)
    print(f"\nOutputs saved to:")
    print(f"  Data:    output/data/")
    print(f"  Figures: output/figures/")
    print(f"  Reports: output/reports/")


if __name__ == "__main__":
    main()
