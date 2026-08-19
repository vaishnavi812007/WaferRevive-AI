import os
import csv
import json
from datetime import datetime


# ============================================================
# WAFERREVIVE-AI
# STEP 26 - AUTOMATED INSPECTION DECISION
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 26")
print("AUTOMATED INSPECTION DECISION")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

INPUT_CSV = (
    r"D:\WaferRevive-AI\results\defect_analysis"
    r"\ranked_defects_002850.csv"
)

OUTPUT_DIR = (
    r"D:\WaferRevive-AI\results\automated_decision"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

JSON_FILE = os.path.join(
    OUTPUT_DIR,
    "automated_decision_002850.json"
)

TXT_FILE = os.path.join(
    OUTPUT_DIR,
    "automated_decision_002850.txt"
)


# ============================================================
# STEP 1 - LOAD DEFECT DATA
# ============================================================

print()
print("1. Loading defect data...")

defects = []

with open(
    INPUT_CSV,
    "r",
    newline=""
) as csv_file:

    reader = csv.DictReader(csv_file)

    for row in reader:

        defects.append({
            "Rank": int(float(row["Rank"])),
            "Defect_ID": int(float(row["Defect_ID"])),
            "Severity": row["Severity"],
            "Priority_Score":
                float(row["Priority_Score"]),
            "Area_pixels":
                int(float(row["Area_pixels"])),
            "Mean_Error":
                float(row["Mean_Error"]),
            "Maximum_Error":
                float(row["Maximum_Error"])
        })


print(
    "Defects loaded :",
    len(defects)
)


# ============================================================
# STEP 2 - CALCULATE STATISTICS
# ============================================================

print()
print("2. Calculating inspection statistics...")

total_defects = len(defects)

total_area = sum(
    d["Area_pixels"]
    for d in defects
)

high_count = sum(
    1
    for d in defects
    if d["Severity"] == "HIGH"
)

medium_count = sum(
    1
    for d in defects
    if d["Severity"] == "MEDIUM"
)

low_count = sum(
    1
    for d in defects
    if d["Severity"] == "LOW"
)

maximum_error = max(
    (
        d["Maximum_Error"]
        for d in defects
    ),
    default=0
)


# ============================================================
# STEP 3 - AUTOMATED DECISION LOGIC
# ============================================================

print()
print("3. Applying automated inspection rules...")

if high_count > 0:

    decision = "DEFECTIVE"

    reason = (
        "One or more HIGH severity defects "
        "were detected."
    )

elif medium_count > 0:

    decision = "REVIEW REQUIRED"

    reason = (
        "MEDIUM severity defects were detected "
        "and require inspection review."
    )

elif low_count > 0:

    decision = "MINOR DEFECTS"

    reason = (
        "Only LOW severity defects were detected."
    )

else:

    decision = "PASS"

    reason = (
        "No significant defects were detected."
    )


# ============================================================
# STEP 4 - HIGHEST PRIORITY DEFECT
# ============================================================

if defects:

    highest = max(
        defects,
        key=lambda x: x["Priority_Score"]
    )

    highest_defect_id = highest["Defect_ID"]

    highest_severity = highest["Severity"]

    highest_score = highest["Priority_Score"]

else:

    highest_defect_id = None

    highest_severity = None

    highest_score = 0


# ============================================================
# STEP 5 - CREATE DECISION DATA
# ============================================================

decision_data = {

    "project":
        "WaferRevive-AI",

    "step":
        26,

    "inspection_image":
        "002850",

    "decision":
        decision,

    "reason":
        reason,

    "statistics": {

        "total_defects":
            total_defects,

        "total_defect_area_pixels":
            total_area,

        "high_severity":
            high_count,

        "medium_severity":
            medium_count,

        "low_severity":
            low_count,

        "maximum_error":
            maximum_error
    },

    "highest_priority_defect": {

        "defect_id":
            highest_defect_id,

        "severity":
            highest_severity,

        "priority_score":
            highest_score
    },

    "generated_at":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
}


# ============================================================
# STEP 6 - SAVE JSON
# ============================================================

print()
print("4. Saving machine-readable decision...")

with open(
    JSON_FILE,
    "w"
) as json_file:

    json.dump(
        decision_data,
        json_file,
        indent=4
    )

print(
    "JSON saved:"
)

print(
    JSON_FILE
)


# ============================================================
# STEP 7 - SAVE HUMAN-READABLE REPORT
# ============================================================

print()
print("5. Creating decision report...")

with open(
    TXT_FILE,
    "w"
) as report:

    report.write(
        "WAFERREVIVE-AI\n"
    )

    report.write(
        "AUTOMATED INSPECTION DECISION\n"
    )

    report.write(
        "============================================================\n\n"
    )

    report.write(
        "INSPECTION IMAGE : 002850\n\n"
    )

    report.write(
        "FINAL DECISION\n"
    )

    report.write(
        "--------------\n"
    )

    report.write(
        decision + "\n\n"
    )

    report.write(
        "REASON\n"
    )

    report.write(
        "------\n"
    )

    report.write(
        reason + "\n\n"
    )

    report.write(
        "STATISTICS\n"
    )

    report.write(
        "----------\n"
    )

    report.write(
        "Total defects     : %d\n"
        % total_defects
    )

    report.write(
        "Defect area       : %d pixels\n"
        % total_area
    )

    report.write(
        "HIGH defects      : %d\n"
        % high_count
    )

    report.write(
        "MEDIUM defects    : %d\n"
        % medium_count
    )

    report.write(
        "LOW defects       : %d\n"
        % low_count
    )

    report.write(
        "Maximum error     : %.6f\n\n"
        % maximum_error
    )

    report.write(
        "HIGHEST PRIORITY DEFECT\n"
    )

    report.write(
        "-----------------------\n"
    )

    report.write(
        "Defect ID         : %s\n"
        % str(highest_defect_id)
    )

    report.write(
        "Severity          : %s\n"
        % str(highest_severity)
    )

    report.write(
        "Priority score    : %.4f\n\n"
        % highest_score
    )

    report.write(
        "Generated by WaferRevive-AI\n"
    )


# ============================================================
# STEP 8 - FINAL OUTPUT
# ============================================================

print()
print("============================================================")
print("STEP 26 - AUTOMATED DECISION RESULT")
print("============================================================")

print(
    "FINAL DECISION :",
    decision
)

print(
    "REASON         :",
    reason
)

print()
print(
    "Total defects  :",
    total_defects
)

print(
    "HIGH           :",
    high_count
)

print(
    "MEDIUM         :",
    medium_count
)

print(
    "LOW            :",
    low_count
)

print()
print(
    "Highest priority defect :",
    highest_defect_id
)

print()
print("Output files:")
print(JSON_FILE)
print(TXT_FILE)

print()
print("============================================================")
print("STEP 26 COMPLETED SUCCESSFULLY")
print("============================================================")