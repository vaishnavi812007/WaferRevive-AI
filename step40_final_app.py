import os
import streamlit as st


# ============================================================
# WAFERREVIVE-AI
# STEP 40 - FINAL SYSTEM INTEGRATION
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


BASE = r"D:\WaferRevive-AI"


# ============================================================
# HOME PAGE
# ============================================================

def home():

    st.title("🔬 WaferRevive-AI")

    st.subheader(
        "AI-Powered Semiconductor Wafer Inspection Platform"
    )

    st.markdown(
        """
        ### 🚀 Complete Inspection System

        WaferRevive-AI combines AI wafer restoration,
        defect detection, quality analysis, visualization,
        history, batch inspection and professional reporting
        into one unified application.
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
            "Batch Analysis",
            "READY"
        )

    with c4:
        st.metric(
            "Reports",
            "READY"
        )

    st.divider()

    st.header("🧭 Available Modules")

    modules = [
        (
            "🆕 New Inspection",
            "Upload a wafer and run the complete AI inspection."
        ),
        (
            "📚 Inspection History",
            "View previously completed inspections."
        ),
        (
            "📦 Batch Inspection",
            "Inspect multiple wafers automatically."
        ),
        (
            "📊 Batch Analytics",
            "Analyze inspection statistics and trends."
        ),
        (
            "📋 Professional Reports",
            "Generate and download inspection reports."
        ),
        (
            "ℹ️ System Information",
            "View project and environment information."
        ),
    ]

    for title, description in modules:

        st.markdown(
            f"### {title}"
        )

        st.write(
            description
        )

    st.divider()

    st.success(
        "✅ WaferRevive-AI Final Integrated System"
    )

    st.caption(
        "Step 40 - Final System Integration"
    )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def system_information():

    st.title(
        "ℹ️ System Information"
    )

    st.header(
        "🔬 WaferRevive-AI"
    )

    st.write(
        "**Platform:** AI Semiconductor Wafer Inspection"
    )

    st.write(
        "**Integration:** Step 40"
    )

    st.write(
        "**Project Directory:**"
    )

    st.code(
        BASE
    )

    st.divider()

    st.header(
        "📁 Project Components"
    )

    files = [
        "step32_full_inspection.py",
        "step33_inspection_history.py",
        "step34_professional_dashboard.py",
        "step35_batch_inspection.py",
        "step38_unified_dashboard.py",
        "step39_professional_report.py",
    ]

    rows = []

    for filename in files:

        path = os.path.join(
            BASE,
            filename
        )

        rows.append(
            {
                "Component": filename,
                "Status": (
                    "✅ Available"
                    if os.path.exists(path)
                    else "⚠️ Not Found"
                )
            }
        )

    import pandas as pd

    df = pd.DataFrame(rows)

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
            "full_inspection"
        ),
        os.path.join(
            "results",
            "batch_inspection"
        ),
        os.path.join(
            "results",
            "inspection_history"
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
# SAFE PAGE LOADER
# ============================================================

def make_page(
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
# PAGE DEFINITIONS
# ============================================================

new_inspection = make_page(
    "step38_unified_dashboard.py",
    "New Inspection",
    "🆕"
)

inspection_history = make_page(
    "step33_inspection_history.py",
    "Inspection History",
    "📚"
)

batch_inspection = make_page(
    "step35_batch_inspection.py",
    "Batch Inspection",
    "📦"
)

professional_dashboard = make_page(
    "step34_professional_dashboard.py",
    "Professional Dashboard",
    "📊"
)

professional_report = make_page(
    "step39_professional_report.py",
    "Professional Reports",
    "📋"
)


# ============================================================
# NAVIGATION
# ============================================================

pages = {
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


if new_inspection is not None:

    pages[
        "Inspection"
    ].append(
        new_inspection
    )


if inspection_history is not None:

    pages[
        "Inspection"
    ].append(
        inspection_history
    )


if batch_inspection is not None:

    pages[
        "Analysis"
    ].append(
        batch_inspection
    )


if professional_dashboard is not None:

    pages[
        "Analysis"
    ].append(
        professional_dashboard
    )


if professional_report is not None:

    pages[
        "Reports"
    ].append(
        professional_report
    )


# ============================================================
# RUN NAVIGATION
# ============================================================

pg = st.navigation(
    pages,
    position="sidebar"
)


# ============================================================
# SIDEBAR BRANDING
# ============================================================

with st.sidebar:

    st.divider()

    st.markdown(
        "### 🔬 WaferRevive-AI"
    )

    st.caption(
        "AI Wafer Inspection Platform"
    )

    st.divider()

    st.caption(
        "Integrated System"
    )

    st.caption(
        "Step 40"
    )

    st.divider()

    st.caption(
        "© WaferRevive-AI"
    )


pg.run()