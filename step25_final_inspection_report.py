import os
import csv
from datetime import datetime


# ============================================================
# WAFERREVIVE-AI
# STEP 25 - FINAL INSPECTION REPORT
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 25")
print("FINAL INSPECTION REPORT")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

INPUT_CSV = (
    r"D:\WaferRevive-AI\results\defect_analysis"
    r"\ranked_defects_002850.csv"
)

OUTPUT_DIR = (
    r"D:\WaferRevive-AI\results\final_inspection"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

REPORT_FILE = os.path.join(
    OUTPUT_DIR,
    "final_inspection_report_002850.txt"
)

SUMMARY_CSV = os.path.join(
    OUTPUT_DIR,
    "final_inspection_summary_002850.csv"
)


# ============================================================
# STEP 1 - LOAD RANKED DEFECT DATA
# ============================================================

print()
print("1. Loading Step 24 ranked defects...")

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
# STEP 2 - CALCULATE FINAL STATISTICS
# ============================================================

print()
print("2. Calculating final inspection statistics...")

total_defects = len(defects)

total_area = sum(
    defect["Area_pixels"]
    for defect in defects
)

high_count = sum(
    1
    for defect in defects
    if defect["Severity"] == "HIGH"
)

medium_count = sum(
    1
    for defect in defects
    if defect["Severity"] == "MEDIUM"
)

low_count = sum(
    1
    for defect in defects
    if defect["Severity"] == "LOW"
)

highest_priority = (
    defects[0]
    if defects
    else None
)

highest_error = max(
    (
        defect["Maximum_Error"]
        for defect in defects
    ),
    default=0
)


# ============================================================
# STEP 3 - DETERMINE INSPECTION STATUS
# ============================================================

print()
print("3. Determining overall inspection status...")

if high_count > 0:

    inspection_status = "DEFECTIVE"

elif medium_count > 0:

    inspection_status = "REVIEW REQUIRED"

elif low_count > 0:

    inspection_status = "MINOR DEFECTS"

else:

    inspection_status = "PASS"


# ============================================================
# STEP 4 - SAVE SUMMARY CSV
# ============================================================

print()
print("4. Saving final summary...")

with open(
    SUMMARY_CSV,
    "w",
    newline=""
) as csv_file:

    writer = csv.writer(csv_file)

    writer.writerow([
        "Parameter",
        "Value"
    ])

    writer.writerow([
        "Inspection_Status",
        inspection_status
    ])

    writer.writerow([
        "Total_Defects",
        total_defects
    ])

    writer.writerow([
        "Total_Defect_Area_Pixels",
        total_area
    ])

    writer.writerow([
        "High_Severity_Defects",
        high_count
    ])

    writer.writerow([
        "Medium_Severity_Defects",
        medium_count
    ])

    writer.writerow([
        "Low_Severity_Defects",
        low_count
    ])

    writer.writerow([
        "Highest_Priority_Defect",
        highest_priority["Defect_ID"]
        if highest_priority
        else "None"
    ])

    writer.writerow([
        "Highest_Priority_Score",
        "%.4f"
        % (
            highest_priority["Priority_Score"]
            if highest_priority
            else 0
        )
    ])

    writer.writerow([
        "Maximum_Error",
        "%.6f"
        % highest_error
    ])

    writer.writerow([
        "Inspection_Date",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ])


# ============================================================
# STEP 5 - CREATE FINAL TEXT REPORT
# ============================================================

print()
print("5. Creating final inspection report...")

with open(
    REPORT_FILE,
    "w"
) as report:

    report.write(
        "WAFERREVIVE-AI\n"
    )

    report.write(
        "FINAL SEMICONDUCTOR WAFER INSPECTION REPORT\n"
    )

    report.write(
        "============================================================\n\n"
    )

    report.write(
        "INSPECTION STATUS\n"
    )

    report.write(
        "-----------------\n"
    )

    report.write(
        "%s\n\n"
        % inspection_status
    )

    report.write(
        "INSPECTION SUMMARY\n"
    )

    report.write(
        "------------------\n"
    )

    report.write(
        "Total defects detected : %d\n"
        % total_defects
    )

    report.write(
        "Total defect area      : %d pixels\n"
        % total_area
    )

    report.write(
        "HIGH severity defects  : %d\n"
        % high_count
    )

    report.write(
        "MEDIUM severity defects: %d\n"
        % medium_count
    )

    report.write(
        "LOW severity defects   : %d\n"
        % low_count
    )

    report.write(
        "Maximum error          : %.6f\n\n"
        % highest_error
    )

    if highest_priority:

        report.write(
            "HIGHEST PRIORITY DEFECT\n"
        )

        report.write(
            "-----------------------\n"
        )

        report.write(
            "Defect ID       : %d\n"
            % highest_priority["Defect_ID"]
        )

        report.write(
            "Severity        : %s\n"
            % highest_priority["Severity"]
        )

        report.write(
            "Priority Score  : %.4f\n"
            % highest_priority["Priority_Score"]
        )

        report.write(
            "Area            : %d pixels\n"
            % highest_priority["Area_pixels"]
        )

        report.write(
            "Maximum Error   : %.6f\n\n"
            % highest_priority["Maximum_Error"]
        )


    report.write(
        "DEFECT RANKING\n"
    )

    report.write(
        "--------------\n"
    )

    for defect in defects:

        report.write(
            "Rank %d | Defect %d | %s | "
            "Score %.4f | Area %d | "
            "Max Error %.6f\n"
            % (
                defect["Rank"],
                defect["Defect_ID"],
                defect["Severity"],
                defect["Priority_Score"],
                defect["Area_pixels"],
                defect["Maximum_Error"]
            )
        )


    report.write(
        "\n============================================================\n"
    )

    report.write(
        "Generated by WaferRevive-AI\n"
    )


# ============================================================
# STEP 6 - PRINT FINAL RESULT
# ============================================================

print()
print("============================================================")
print("STEP 25 - FINAL INSPECTION RESULT")
print("============================================================")

print(
    "Inspection status :",
    inspection_status
)

print(
    "Total defects     :",
    total_defects
)

print(
    "Total defect area :",
    total_area,
    "pixels"
)

print(
    "HIGH              :",
    high_count
)

print(
    "MEDIUM            :",
    medium_count
)

print(
    "LOW               :",
    low_count
)

if highest_priority:

    print()
    print(
        "Highest priority defect :",
        highest_priority["Defect_ID"]
    )

    print(
        "Priority score          :",
        "%.4f"
        % highest_priority["Priority_Score"]
    )

print()
print("Output files:")
print(REPORT_FILE)
print(SUMMARY_CSV)

print()
print("============================================================")
print("STEP 25 COMPLETED SUCCESSFULLY")
print("============================================================")