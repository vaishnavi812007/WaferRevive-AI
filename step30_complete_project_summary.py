import os
import csv


# ============================================================
# WAFERREVIVE-AI
# STEP 30 - COMPLETE PROJECT SUMMARY
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 30")
print("COMPLETE PROJECT SUMMARY")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

QUALITY_CSV = (
    r"D:\WaferRevive-AI\results\wafer_quality"
    r"\wafer_quality_score_002850.csv"
)

DECISION_TXT = (
    r"D:\WaferRevive-AI\results\automated_decision"
    r"\automated_decision_002850.txt"
)

DEFECT_CSV = (
    r"D:\WaferRevive-AI\results\defect_analysis"
    r"\ranked_defects_002850.csv"
)

OUTPUT_DIR = (
    r"D:\WaferRevive-AI\results\project_summary"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

SUMMARY_FILE = os.path.join(
    OUTPUT_DIR,
    "complete_project_summary_002850.txt"
)

SUMMARY_CSV = os.path.join(
    OUTPUT_DIR,
    "complete_project_summary_002850.csv"
)


# ============================================================
# STEP 1 - LOAD QUALITY DATA
# ============================================================

print()
print("1. Loading wafer quality results...")

quality = {}

with open(
    QUALITY_CSV,
    "r",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        quality[row["Parameter"]] = row["Value"]


quality_score = float(
    quality["Quality_Score"]
)

quality_grade = quality[
    "Quality_Grade"
]

quality_status = quality[
    "Quality_Status"
]

total_defects = int(
    float(quality["Total_Defects"])
)

high_count = int(
    float(quality["High_Defects"])
)

medium_count = int(
    float(quality["Medium_Defects"])
)

low_count = int(
    float(quality["Low_Defects"])
)

defect_area = int(
    float(quality["Total_Defect_Area"])
)

area_percentage = float(
    quality["Defect_Area_Percentage"]
)

maximum_error = float(
    quality["Maximum_Error"]
)


# ============================================================
# STEP 2 - LOAD RANKED DEFECTS
# ============================================================

print()
print("2. Loading defect ranking...")

defects = []

with open(
    DEFECT_CSV,
    "r",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        defects.append({
            "Rank": int(float(row["Rank"])),
            "Defect_ID": int(float(row["Defect_ID"])),
            "Severity": row["Severity"],
            "Priority_Score":
                float(row["Priority_Score"]),
            "Area_pixels":
                int(float(row["Area_pixels"])),
            "Maximum_Error":
                float(row["Maximum_Error"])
        })


print(
    "Defects loaded :",
    len(defects)
)


# ============================================================
# STEP 3 - TOP DEFECT
# ============================================================

if defects:

    top_defect = defects[0]

else:

    top_defect = None


# ============================================================
# STEP 4 - CREATE PROJECT SUMMARY
# ============================================================

print()
print("3. Creating complete project summary...")

with open(
    SUMMARY_FILE,
    "w"
) as file:

    file.write(
        "WAFERREVIVE-AI\n"
    )

    file.write(
        "COMPLETE PROJECT SUMMARY\n"
    )

    file.write(
        "============================================================\n\n"
    )

    file.write(
        "PROJECT STATUS\n"
    )

    file.write(
        "--------------\n"
    )

    file.write(
        "Pipeline status : COMPLETED\n"
    )

    file.write(
        "Inspection status: %s\n\n"
        % quality_status
    )

    file.write(
        "FINAL QUALITY\n"
    )

    file.write(
        "-------------\n"
    )

    file.write(
        "Quality score : %.2f / 100\n"
        % quality_score
    )

    file.write(
        "Quality grade : %s\n"
        % quality_grade
    )

    file.write(
        "Maximum error : %.6f\n\n"
        % maximum_error
    )

    file.write(
        "DEFECT SUMMARY\n"
    )

    file.write(
        "--------------\n"
    )

    file.write(
        "Total defects : %d\n"
        % total_defects
    )

    file.write(
        "HIGH          : %d\n"
        % high_count
    )

    file.write(
        "MEDIUM        : %d\n"
        % medium_count
    )

    file.write(
        "LOW           : %d\n"
        % low_count
    )

    file.write(
        "Defect area   : %d pixels\n"
        % defect_area
    )

    file.write(
        "Area ratio    : %.4f%%\n\n"
        % area_percentage
    )

    if top_defect:

        file.write(
            "TOP PRIORITY DEFECT\n"
        )

        file.write(
            "-------------------\n"
        )

        file.write(
            "Defect ID      : %d\n"
            % top_defect["Defect_ID"]
        )

        file.write(
            "Severity       : %s\n"
            % top_defect["Severity"]
        )

        file.write(
            "Priority score : %.4f\n"
            % top_defect["Priority_Score"]
        )

        file.write(
            "Area           : %d pixels\n"
            % top_defect["Area_pixels"]
        )

        file.write(
            "Maximum error  : %.6f\n\n"
            % top_defect["Maximum_Error"]
        )

    file.write(
        "PIPELINE\n"
    )

    file.write(
        "--------\n"
    )

    file.write(
        "Step 23 : Refined defect detection - COMPLETED\n"
    )

    file.write(
        "Step 24 : Defect analysis and ranking - COMPLETED\n"
    )

    file.write(
        "Step 25 : Final inspection report - COMPLETED\n"
    )

    file.write(
        "Step 26 : Automated inspection decision - COMPLETED\n"
    )

    file.write(
        "Step 27 : Inspection dashboard - COMPLETED\n"
    )

    file.write(
        "Step 28 : Wafer quality score - COMPLETED\n"
    )

    file.write(
        "Step 29 : Quality visualization - COMPLETED\n"
    )

    file.write(
        "Step 30 : Complete project summary - COMPLETED\n"
    )


# ============================================================
# STEP 5 - SAVE CSV SUMMARY
# ============================================================

print()
print("4. Saving summary CSV...")

with open(
    SUMMARY_CSV,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Parameter",
        "Value"
    ])

    writer.writerow([
        "Pipeline_Status",
        "COMPLETED"
    ])

    writer.writerow([
        "Inspection_Status",
        quality_status
    ])

    writer.writerow([
        "Quality_Score",
        "%.2f" % quality_score
    ])

    writer.writerow([
        "Quality_Grade",
        quality_grade
    ])

    writer.writerow([
        "Total_Defects",
        total_defects
    ])

    writer.writerow([
        "High_Defects",
        high_count
    ])

    writer.writerow([
        "Medium_Defects",
        medium_count
    ])

    writer.writerow([
        "Low_Defects",
        low_count
    ])

    writer.writerow([
        "Defect_Area",
        defect_area
    ])

    writer.writerow([
        "Defect_Area_Percentage",
        "%.4f" % area_percentage
    ])

    writer.writerow([
        "Maximum_Error",
        "%.6f" % maximum_error
    ])

    if top_defect:

        writer.writerow([
            "Top_Defect_ID",
            top_defect["Defect_ID"]
        ])

        writer.writerow([
            "Top_Defect_Severity",
            top_defect["Severity"]
        ])

        writer.writerow([
            "Top_Defect_Priority",
            "%.4f"
            % top_defect["Priority_Score"]
        ])


# ============================================================
# STEP 6 - FINAL OUTPUT
# ============================================================

print()
print("============================================================")
print("STEP 30 - COMPLETE PROJECT RESULT")
print("============================================================")

print(
    "Pipeline status   : COMPLETED"
)

print(
    "Inspection status :",
    quality_status
)

print(
    "Quality score     :",
    "%.2f / 100"
    % quality_score
)

print(
    "Quality grade     :",
    quality_grade
)

print(
    "Total defects     :",
    total_defects
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

print(
    "Defect area       :",
    defect_area,
    "pixels"
)

if top_defect:

    print(
        "Top defect        :",
        top_defect["Defect_ID"]
    )

print()
print("Output files:")
print(SUMMARY_FILE)
print(SUMMARY_CSV)

print()
print("============================================================")
print("STEP 30 COMPLETED SUCCESSFULLY")
print("============================================================")