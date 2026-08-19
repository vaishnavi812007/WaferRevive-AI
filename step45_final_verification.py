import os
import sys
import subprocess
from datetime import datetime


# ============================================================
# WAFERREVIVE-AI
# STEP 45 - FINAL RELEASE & VERIFICATION
# ============================================================

BASE = r"D:\WaferRevive-AI"


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("WAFERREVIVE-AI - STEP 45")
print("FINAL RELEASE & VERIFICATION")
print("=" * 70)

print()
print("Project directory:")
print(BASE)


# ============================================================
# IMPORTANT FILES
# ============================================================

required_files = [

    "models\\best_model.pth",

    "step23_refined_defects.py",
    "step24_defect_analysis.py",
    "step25_final_inspection_report.py",
    "step26_automated_decision.py",
    "step27_inspection_dashboard.py",
    "step28_wafer_quality_score.py",
    "step29_quality_visualization.py",
    "step30_complete_project_summary.py",

    "step31_app.py",

    "step32_full_inspection.py",
    "step33_inspection_history.py",
    "step34_professional_dashboard.py",
    "step35_batch_inspection.py",
    "step36_batch_report.py",
    "step37_batch_quality_analytics.py",
    "step38_unified_dashboard.py",
    "step39_professional_report.py",
    "step40_final_app.py",
    "step42_final_analytics.py",
    "step43_final_integrated_app.py",
    "step44_professional_ui.py",
    "step45_final_verification.py"
]


# ============================================================
# FILE CHECK
# ============================================================

print()
print("1. Checking required project files...")
print()

missing_files = []
available_files = []

for relative_path in required_files:

    full_path = os.path.join(
        BASE,
        relative_path
    )

    if os.path.exists(full_path):

        available_files.append(
            relative_path
        )

        print(
            "  [OK]      ",
            relative_path
        )

    else:

        missing_files.append(
            relative_path
        )

        print(
            "  [MISSING] ",
            relative_path
        )


# ============================================================
# PYTHON SYNTAX CHECK
# ============================================================

print()
print("2. Checking Python syntax...")
print()

python_files = [

    "step23_refined_defects.py",
    "step24_defect_analysis.py",
    "step25_final_inspection_report.py",
    "step26_automated_decision.py",
    "step27_inspection_dashboard.py",
    "step28_wafer_quality_score.py",
    "step29_quality_visualization.py",
    "step30_complete_project_summary.py",
    "step31_app.py",
    "step32_full_inspection.py",
    "step33_inspection_history.py",
    "step34_professional_dashboard.py",
    "step35_batch_inspection.py",
    "step36_batch_report.py",
    "step37_batch_quality_analytics.py",
    "step38_unified_dashboard.py",
    "step39_professional_report.py",
    "step40_final_app.py",
    "step42_final_analytics.py",
    "step43_final_integrated_app.py",
    "step44_professional_ui.py",
    "step45_final_verification.py"
]

syntax_failed = []


for filename in python_files:

    path = os.path.join(
        BASE,
        filename
    )

    if not os.path.exists(path):

        continue

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            path
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        print(
            "  [OK]      ",
            filename
        )

    else:

        syntax_failed.append(
            filename
        )

        print(
            "  [ERROR]   ",
            filename
        )

        if result.stderr:

            print(
                result.stderr.strip()
            )


# ============================================================
# MODEL CHECK
# ============================================================

print()
print("3. Checking AI model...")
print()

model_path = os.path.join(
    BASE,
    "models",
    "best_model.pth"
)

if os.path.exists(model_path):

    model_size = os.path.getsize(
        model_path
    )

    print(
        "  [OK] Model found"
    )

    print(
        "  Model size:",
        model_size,
        "bytes"
    )

else:

    print(
        "  [ERROR] Model not found"
    )


# ============================================================
# RESULT DIRECTORIES
# ============================================================

print()
print("4. Checking result directories...")
print()

result_directories = [

    "results",

    "results\\full_inspection",

    "results\\batch_inspection",

    "results\\inspection_history",

    "results\\professional_reports",

    "results\\batch_quality_analytics"
]


missing_directories = []


for relative_path in result_directories:

    path = os.path.join(
        BASE,
        relative_path
    )

    if os.path.exists(path):

        try:

            count = len(
                os.listdir(path)
            )

        except Exception:

            count = 0

        print(
            "  [OK]      ",
            relative_path,
            "| files:",
            count
        )

    else:

        missing_directories.append(
            relative_path
        )

        print(
            "  [MISSING] ",
            relative_path
        )


# ============================================================
# INSPECTION OUTPUT CHECK
# ============================================================

print()
print("5. Checking generated inspection outputs...")
print()

output_patterns = [

    (
        "Full inspection",
        "results\\full_inspection"
    ),

    (
        "Batch inspection",
        "results\\batch_inspection"
    ),

    (
        "Inspection history",
        "results\\inspection_history"
    ),

    (
        "Professional reports",
        "results\\professional_reports"
    ),

    (
        "Batch analytics",
        "results\\batch_quality_analytics"
    )
]


for label, relative_path in output_patterns:

    path = os.path.join(
        BASE,
        relative_path
    )

    if not os.path.exists(path):

        print(
            "  [INFO]    ",
            label,
            "- folder not present"
        )

        continue

    files = []

    for root, dirs, filenames in os.walk(path):

        for filename in filenames:

            files.append(
                os.path.join(
                    root,
                    filename
                )
            )

    print(
        "  [OK]      ",
        label,
        "| outputs:",
        len(files)
    )


# ============================================================
# MAIN APPLICATION CHECK
# ============================================================

print()
print("6. Checking final application...")
print()

main_app = os.path.join(
    BASE,
    "step44_professional_ui.py"
)

if os.path.exists(main_app):

    print(
        "  [OK] Final professional UI exists"
    )

    print(
        "  Launch command:"
    )

    print(
        "  python -m streamlit run step44_professional_ui.py"
    )

else:

    print(
        "  [ERROR] Final professional UI not found"
    )


# ============================================================
# RELEASE SUMMARY
# ============================================================

print()
print("=" * 70)
print("STEP 45 - FINAL VERIFICATION SUMMARY")
print("=" * 70)

print()

print(
    "Required files found :",
    len(available_files),
    "/",
    len(required_files)
)

print(
    "Missing files        :",
    len(missing_files)
)

print(
    "Syntax failures      :",
    len(syntax_failed)
)

print(
    "Missing directories  :",
    len(missing_directories)
)


# ============================================================
# RELEASE STATUS
# ============================================================

if (
    len(missing_files) == 0
    and
    len(syntax_failed) == 0
):

    release_status = "READY"

else:

    release_status = "REVIEW REQUIRED"


print()
print(
    "FINAL RELEASE STATUS :",
    release_status
)


# ============================================================
# FINAL COMMAND
# ============================================================

print()

if release_status == "READY":

    print(
        "============================================================"
    )

    print(
        "WAFERREVIVE-AI FINAL RELEASE READY"
    )

    print(
        "============================================================"
    )

    print()
    print(
        "Start the final application with:"
    )

    print()
    print(
        "python -m streamlit run step44_professional_ui.py"
    )

else:

    print(
        "============================================================"
    )

    print(
        "WAFERREVIVE-AI NEEDS REVIEW"
    )

    print(
        "============================================================"
    )

    print()
    print(
        "Review the missing/error items above."
    )


# ============================================================
# TIMESTAMP
# ============================================================

print()
print(
    "Verification time:",
    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)

print()
print("=" * 70)
print("STEP 45 COMPLETED")
print("=" * 70)