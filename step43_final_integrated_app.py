import os
import streamlit as st


# ============================================================
# WAFERREVIVE-AI
# STEP 43 - FINAL INTEGRATED APPLICATION
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


BASE = r"D:\WaferRevive-AI"


# ============================================================
# HOME
# ============================================================

def home():

    st.title("🔬 WaferRevive-AI")

    st.subheader(
        "AI-Powered Semiconductor Wafer Inspection Platform"
    )

    st.markdown(
        """
        ## Welcome to WaferRevive-AI

        A complete AI-powered platform for semiconductor
        wafer inspection, defect analysis, quality assessment,
        batch processing, analytics and professional reporting.
        """
    )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "AI Inspection",
            "READY"
        )

    with c2:
        st.metric(
            "Visual Outputs",
            "6"
        )

    with c3:
        st.metric(
            "Analytics",
            "READY"
        )

    with c4:
        st.metric(
            "Reports",
            "READY"
        )

    st.divider()

    st.header(
        "🧭 System Modules"
    )

    modules = [
        (
            "🆕 New Inspection",
            "Upload a wafer and perform the complete AI inspection."
        ),
        (
            "📚 Inspection History",
            "Review previous inspection results."
        ),
        (
            "📦 Batch Inspection",
            "Process multiple wafers in one workflow."
        ),
        (
            "📊 Analytics",
            "Analyze quality, defects, severity and trends."
        ),
        (
            "📊 Professional Dashboard",
            "View detailed inspection analysis."
        ),
        (
            "📋 Professional Reports",
            "Generate and download professional reports."
        ),
    ]

    for title, description in modules:

        with st.container():

            st.markdown(
                f"### {title}"
            )

            st.write(
                description
            )

    st.divider()

    st.success(
        "✅ WaferRevive-AI Integrated System Ready"
    )

    st.caption(
        "Step 43 — Final Integrated Application"
    )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def system_information():

    import pandas as pd

    st.title(
        "ℹ️ System Information"
    )

    st.subheader(
        "WaferRevive-AI Project Status"
    )

    st.write(
        "**Project Directory:**"
    )

    st.code(
        BASE
    )

    st.divider()

    files = [
        (
            "Step 32",
            "step32_full_inspection.py"
        ),
        (
            "Step 33",
            "step33_inspection_history.py"
        ),
        (
            "Step 34",
            "step34_professional_dashboard.py"
        ),
        (
            "Step 35",
            "step35_batch_inspection.py"
        ),
        (
            "Step 38",
            "step38_unified_dashboard.py"
        ),
        (
            "Step 39",
            "step39_professional_report.py"
        ),
        (
            "Step 40",
            "step40_final_app.py"
        ),
        (
            "Step 42",
            "step42_final_analytics.py"
        ),
        (
            "Step 43",
            "step43_final_integrated_app.py"
        ),
    ]

    rows = []

    for step, filename in files:

        path = os.path.join(
            BASE,
            filename
        )

        rows.append(
            {
                "Step": step,
                "File": filename,
                "Status": (
                    "✅ Available"
                    if os.path.exists(path)
                    else "❌ Missing"
                )
            }
        )

    df = pd.DataFrame(
        rows
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.header(
        "📂 Results Directories"
    )

    directories = [
        "results",
        os.path.join(
            "results",
            "inspection_history"
        ),
        os.path.join(
            "results",
            "batch_inspection"
        ),
        os.path.join(
            "results",
            "professional_reports"
        ),
    ]

    for directory in directories:

        path = os.path.join(
            BASE,
            directory
        )

        if os.path.exists(path):

            st.success(
                f"✅ {directory}"
            )

        else:

            st.info(
                f"ℹ️ {directory}"
            )


# ============================================================
# PAGE LOADER
# ============================================================

def external_page(
    filename,
    title,
    icon
):

    path = os.path.join(
        BASE,
        filename
    )

    if os.path.exists(path):

        return st.Page(
            path,
            title=title,
            icon=icon
        )

    return None


# ============================================================
# CREATE PAGES
# ============================================================

new_inspection = external_page(
    "step38_unified_dashboard.py",
    "New Inspection",
    "🆕"
)


history = external_page(
    "step33_inspection_history.py",
    "Inspection History",
    "📚"
)


batch = external_page(
    "step35_batch_inspection.py",
    "Batch Inspection",
    "📦"
)


analytics = external_page(
    "step42_final_analytics.py",
    "Analytics",
    "📊"
)


professional_dashboard = external_page(
    "step34_professional_dashboard.py",
    "Professional Dashboard",
    "📈"
)


reports = external_page(
    "step39_professional_report.py",
    "Professional Reports",
    "📋"
)


# ============================================================
# NAVIGATION STRUCTURE
# ============================================================

navigation = {
    "WaferRevive-AI": [
        st.Page(
            home,
            title="Home",
            icon="🏠",
            default=True
        )
    ],

    "Inspection": [],

    "Analysis": [],

    "Reports": [],

    "System": [
        st.Page(
            system_information,
            title="System Information",
            icon="ℹ️"
        )
    ]
}


# ============================================================
# INSPECTION
# ============================================================

if new_inspection is not None:

    navigation[
        "Inspection"
    ].append(
        new_inspection
    )


if history is not None:

    navigation[
        "Inspection"
    ].append(
        history
    )


# ============================================================
# ANALYSIS
# ============================================================

if batch is not None:

    navigation[
        "Analysis"
    ].append(
        batch
    )


if analytics is not None:

    navigation[
        "Analysis"
    ].append(
        analytics
    )


if professional_dashboard is not None:

    navigation[
        "Analysis"
    ].append(
        professional_dashboard
    )


# ============================================================
# REPORTS
# ============================================================

if reports is not None:

    navigation[
        "Reports"
    ].append(
        reports
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        # 🔬 WaferRevive-AI

        **AI Semiconductor Wafer Inspection**
        """
    )

    st.divider()

    st.caption(
        "FINAL INTEGRATED SYSTEM"
    )

    st.caption(
        "Step 43"
    )

    st.divider()

    st.info(
        "Use the navigation above to access "
        "each part of the inspection platform."
    )

    st.divider()

    st.caption(
        "WaferRevive-AI"
    )


# ============================================================
# RUN APPLICATION
# ============================================================

pg = st.navigation(
    navigation,
    position="sidebar"
)

pg.run()