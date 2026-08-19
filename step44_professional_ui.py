import os
import streamlit as st


# ============================================================
# WAFERREVIVE-AI
# STEP 44 - PROFESSIONAL UI / UX
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = r"D:\WaferRevive-AI"


# ============================================================
# PROFESSIONAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.2);
    }

    /* Metric cards */

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 12px;
        padding: 15px;
    }

    /* Buttons */

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 600;
    }

    /* Expanders */

    div[data-testid="stExpander"] {
        border-radius: 10px;
    }

    /* Tables */

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Footer */

    .wr-footer {
        text-align: center;
        padding: 25px 10px 5px 10px;
        opacity: 0.65;
        font-size: 13px;
    }

    .wr-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        border: 1px solid rgba(128,128,128,0.25);
        font-size: 12px;
        margin-top: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HOME
# ============================================================

def home():

    st.title(
        "🔬 WaferRevive-AI"
    )

    st.subheader(
        "AI-Powered Semiconductor Wafer Inspection Platform"
    )

    st.write(
        "A unified environment for wafer restoration, "
        "defect detection, quality analysis, batch inspection "
        "and professional reporting."
    )

    st.divider()

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    st.header(
        "⚡ System Status"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "AI Inspection",
            "READY"
        )

    with c2:

        st.metric(
            "6 Visual Outputs",
            "READY"
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

    # --------------------------------------------------------
    # MODULES
    # --------------------------------------------------------

    st.header(
        "🧭 Inspection Platform"
    )

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.subheader(
                "🆕 New Inspection"
            )

            st.write(
                "Upload a wafer and perform the complete "
                "AI-powered inspection workflow."
            )

            st.caption(
                "Upload → Restore → Detect → Analyze → Decide"
            )

        with st.container(border=True):

            st.subheader(
                "📚 Inspection History"
            )

            st.write(
                "Review previous inspection results "
                "and inspection records."
            )

        with st.container(border=True):

            st.subheader(
                "📦 Batch Inspection"
            )

            st.write(
                "Process multiple wafer samples "
                "through the inspection pipeline."
            )

    with col2:

        with st.container(border=True):

            st.subheader(
                "📊 Analytics"
            )

            st.write(
                "Explore quality scores, defect severity, "
                "defect area and inspection trends."
            )

        with st.container(border=True):

            st.subheader(
                "📈 Professional Dashboard"
            )

            st.write(
                "Review detailed inspection metrics "
                "and engineering analysis."
            )

        with st.container(border=True):

            st.subheader(
                "📋 Professional Reports"
            )

            st.write(
                "Generate downloadable inspection "
                "reports and result packages."
            )

    st.divider()

    st.success(
        "✅ WaferRevive-AI is ready for inspection."
    )

    st.markdown(
        """
        <div class="wr-footer">
            WaferRevive-AI<br>
            <span class="wr-badge">
                Integrated AI Wafer Inspection Platform
            </span>
        </div>
        """,
        unsafe_allow_html=True
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
        "WaferRevive-AI System Status"
    )

    st.write(
        "**Project Directory**"
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
            "Step 42",
            "step42_final_analytics.py"
        ),
        (
            "Step 43",
            "step43_final_integrated_app.py"
        ),
        (
            "Step 44",
            "step44_professional_ui.py"
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
                "Component": filename,
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
        "📂 Result Storage"
    )

    result_dirs = [
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
        )
    ]

    for directory in result_dirs:

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
# EXTERNAL PAGE HELPER
# ============================================================

def page(
    filename,
    title,
    icon
):

    path = os.path.join(
        BASE,
        filename
    )

    if not os.path.exists(path):

        return None

    return st.Page(
        path,
        title=title,
        icon=icon
    )


# ============================================================
# CREATE NAVIGATION
# ============================================================

new_inspection = page(
    "step38_unified_dashboard.py",
    "New Inspection",
    "🆕"
)

history = page(
    "step33_inspection_history.py",
    "Inspection History",
    "📚"
)

batch = page(
    "step35_batch_inspection.py",
    "Batch Inspection",
    "📦"
)

analytics = page(
    "step42_final_analytics.py",
    "Analytics",
    "📊"
)

dashboard = page(
    "step34_professional_dashboard.py",
    "Professional Dashboard",
    "📈"
)

reports = page(
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


# ============================================================
# INSPECTION
# ============================================================

if new_inspection:

    pages[
        "Inspection"
    ].append(
        new_inspection
    )


if history:

    pages[
        "Inspection"
    ].append(
        history
    )


# ============================================================
# ANALYSIS
# ============================================================

if batch:

    pages[
        "Analysis"
    ].append(
        batch
    )


if analytics:

    pages[
        "Analysis"
    ].append(
        analytics
    )


if dashboard:

    pages[
        "Analysis"
    ].append(
        dashboard
    )


# ============================================================
# REPORTS
# ============================================================

if reports:

    pages[
        "Reports"
    ].append(
        reports
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

with st.sidebar:

    st.markdown(
        """
        # 🔬 WaferRevive-AI

        **Semiconductor Wafer Inspection**
        """
    )

    st.divider()

    st.caption(
        "FINAL PROFESSIONAL INTERFACE"
    )

    st.caption(
        "Step 44"
    )

    st.divider()

    st.markdown(
        """
        **Quick Navigation**

        🆕 New Inspection  
        📚 History  
        📦 Batch  
        📊 Analytics  
        📈 Dashboard  
        📋 Reports
        """
    )

    st.divider()

    st.caption(
        "AI Inspection Platform"
    )


# ============================================================
# RUN
# ============================================================

pg = st.navigation(
    pages,
    position="sidebar"
)

pg.run()