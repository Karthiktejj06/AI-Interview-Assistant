"""
Complete Modern CSS Design System for AI Interview Assistant.
Clean, professional, easy-to-use interface with sidebar navigation.
"""

def inject_custom_css(theme: str = "dark"):
    """Inject complete custom CSS styles for the AI Interview Assistant platform."""

    if theme == "dark":
        bg_primary = "#0F172A"
        bg_secondary = "#1E293B"
        bg_card = "#1E293B"
        bg_card_hover = "#263548"
        text_primary = "#F1F5F9"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        border_color = "#334155"
        border_hover = "#3B82F6"
        input_bg = "#0F172A"
        input_border = "#334155"
        sidebar_bg = "#0F172A"
        shadow_color = "rgba(0,0,0,0.4)"
        success_bg = "rgba(16,185,129,0.12)"
        warning_bg = "rgba(245,158,11,0.12)"
        error_bg = "rgba(239,68,68,0.12)"
        info_bg = "rgba(59,130,246,0.12)"
    else:
        bg_primary = "#F8FAFC"
        bg_secondary = "#FFFFFF"
        bg_card = "#FFFFFF"
        bg_card_hover = "#F1F5F9"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#94A3B8"
        border_color = "#E2E8F0"
        border_hover = "#3B82F6"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"
        sidebar_bg = "#F1F5F9"
        shadow_color = "rgba(0,0,0,0.08)"
        success_bg = "rgba(16,185,129,0.08)"
        warning_bg = "rgba(245,158,11,0.08)"
        error_bg = "rgba(239,68,68,0.08)"
        info_bg = "rgba(59,130,246,0.08)"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ==========================================
       GLOBAL RESET & BASE
    ========================================== */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; }}

    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {bg_primary} !important;
        color: {text_primary} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 14px;
        line-height: 1.6;
    }}

    /* ==========================================
       HIDE DEFAULT STREAMLIT ELEMENTS (DISABLED)
    ========================================== */

    /* Remove Streamlit's default padding */
    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0 !important;
    }}

    [data-testid="block-container"] {{
        padding: 1.5rem 2rem !important;
        max-width: 1400px;
    }}

    /* ==========================================
       SIDEBAR
    ========================================== */

    /* ==========================================
       PAGE TITLE
    ========================================== */
    .page-header {{
        padding: 0 0 1.5rem 0;
        border-bottom: 1px solid {border_color};
        margin-bottom: 1.5rem;
    }}

    .page-title {{
        font-size: 24px;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 4px;
    }}

    .page-subtitle {{
        font-size: 14px;
        color: {text_secondary};
    }}

    /* ==========================================
       CARD COMPONENTS
    ========================================== */
    .card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    .card:hover {{
        border-color: {border_hover};
        box-shadow: 0 4px 20px {shadow_color};
    }}

    .card-title {{
        font-size: 16px;
        font-weight: 600;
        color: {text_primary};
        margin-bottom: 0.5rem;
    }}

    .card-body {{
        font-size: 14px;
        color: {text_secondary};
    }}

    /* ==========================================
       QUICK ACTION CARDS (DASHBOARD)
    ========================================== */
    .action-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        height: 100%;
        transition: all 0.25s ease;
        cursor: default;
    }}

    .action-card:hover {{
        border-color: {border_hover};
        box-shadow: 0 8px 24px {shadow_color};
        transform: translateY(-2px);
    }}

    .action-icon {{
        font-size: 36px;
        margin-bottom: 10px;
        display: block;
    }}

    .action-title {{
        font-size: 15px;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 6px;
    }}

    .action-desc {{
        font-size: 12px;
        color: {text_secondary};
        line-height: 1.5;
    }}

    /* ==========================================
       METRIC CARDS
    ========================================== */
    .metric-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        text-align: center;
    }}

    .metric-label {{
        font-size: 12px;
        font-weight: 600;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }}

    .metric-value {{
        font-size: 28px;
        font-weight: 800;
        color: {text_primary};
        font-variant-numeric: tabular-nums;
    }}

    .metric-sub {{
        font-size: 12px;
        color: {text_muted};
        margin-top: 4px;
    }}

    /* ==========================================
       SCORE DISPLAY (LARGE)
    ========================================== */
    .score-circle {{
        background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%);
        border-radius: 50%;
        width: 110px;
        height: 110px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px;
        box-shadow: 0 4px 16px rgba(59,130,246,0.35);
    }}

    .score-num {{
        font-size: 32px;
        font-weight: 800;
        color: white;
        line-height: 1;
    }}

    .score-denom {{
        font-size: 13px;
        color: rgba(255,255,255,0.75);
    }}

    /* ==========================================
       BADGES / PILLS
    ========================================== */
    .badge {{
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }}

    .badge-blue {{ background: rgba(59,130,246,0.15); color: #60A5FA; }}
    .badge-green {{ background: rgba(16,185,129,0.15); color: #34D399; }}
    .badge-red {{ background: rgba(239,68,68,0.15); color: #F87171; }}
    .badge-yellow {{ background: rgba(245,158,11,0.15); color: #FBBF24; }}
    .badge-purple {{ background: rgba(139,92,246,0.15); color: #A78BFA; }}

    /* Status badges */
    .status-completed {{ background: {success_bg}; color: #10B981; border: 1px solid rgba(16,185,129,0.2); }}
    .status-in_progress {{ background: {warning_bg}; color: #F59E0B; border: 1px solid rgba(245,158,11,0.2); }}

    /* ==========================================
       INTERVIEW HISTORY ROWS
    ========================================== */
    .interview-row {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        transition: border-color 0.2s ease;
    }}

    .interview-row:hover {{
        border-color: {border_hover};
    }}

    /* ==========================================
       QUESTION DISPLAY BOX
    ========================================== */
    .question-box {{
        background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(99,102,241,0.05));
        border: 1px solid rgba(59,130,246,0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }}

    .question-number {{
        font-size: 12px;
        font-weight: 600;
        color: #3B82F6;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }}

    .question-text {{
        font-size: 17px;
        font-weight: 600;
        color: {text_primary};
        line-height: 1.5;
    }}

    .cv-ref-tag {{
        font-size: 11px;
        color: #A78BFA;
        background: rgba(139,92,246,0.12);
        padding: 2px 8px;
        border-radius: 10px;
        display: inline-block;
        margin-top: 8px;
    }}

    /* ==========================================
       EVALUATION RESULT BOX
    ========================================== */
    .eval-box {{
        background: {success_bg};
        border: 1px solid rgba(16,185,129,0.2);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }}

    .score-breakdown {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
    }}

    .score-item {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
        min-width: 90px;
    }}

    .score-item-label {{
        font-size: 10px;
        color: {text_muted};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .score-item-value {{
        font-size: 20px;
        font-weight: 700;
        color: {text_primary};
    }}

    /* ==========================================
       RECOMMENDATION CARDS
    ========================================== */
    .rec-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 12px;
    }}

    .rec-priority-high {{
        border-left: 4px solid #EF4444;
    }}

    .rec-priority-medium {{
        border-left: 4px solid #F59E0B;
    }}

    .rec-priority-low {{
        border-left: 4px solid #10B981;
    }}

    .rec-action {{
        font-size: 15px;
        font-weight: 600;
        color: {text_primary};
        margin-bottom: 4px;
    }}

    .rec-reason {{
        font-size: 13px;
        color: {text_secondary};
    }}

    /* ==========================================
       READINESS BANNER
    ========================================== */
    .readiness-ready {{
        background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(5,150,105,0.08));
        border: 1px solid rgba(16,185,129,0.3);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }}

    .readiness-almost {{
        background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(217,119,6,0.08));
        border: 1px solid rgba(245,158,11,0.3);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }}

    .readiness-needs {{
        background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(185,28,28,0.08));
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }}

    .readiness-title {{
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 6px;
    }}

    .readiness-score {{
        font-size: 42px;
        font-weight: 900;
        line-height: 1;
    }}

    /* ==========================================
       LEARNING PATH CARD
    ========================================== */
    .learning-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .learning-icon {{
        font-size: 24px;
        flex-shrink: 0;
    }}

    .learning-topic {{
        font-size: 14px;
        font-weight: 600;
        color: {text_primary};
    }}

    .learning-time {{
        font-size: 12px;
        color: {text_muted};
    }}

    /* ==========================================
       WELCOME/HERO SECTION (Compact)
    ========================================== */
    .welcome-strip {{
        background: linear-gradient(135deg, #1E3A5F 0%, #1E293B 100%);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }}

    .welcome-name {{
        font-size: 20px;
        font-weight: 700;
        color: #F1F5F9;
    }}

    .welcome-sub {{
        font-size: 13px;
        color: #94A3B8;
        margin-top: 3px;
    }}

    /* ==========================================
       DIVIDER
    ========================================== */
    .section-divider {{
        border: none;
        border-top: 1px solid {border_color};
        margin: 1.5rem 0;
    }}

    .section-label {{
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {text_muted};
        margin-bottom: 0.75rem;
    }}

    /* ==========================================
       STREAMLIT OVERRIDES
    ========================================== */
    /* Buttons */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        border: 1px solid {border_color} !important;
    }}

    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
        border-color: transparent !important;
        color: white !important;
        box-shadow: 0 2px 10px rgba(59,130,246,0.3) !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 4px 18px rgba(59,130,246,0.45) !important;
        transform: translateY(-1px) !important;
    }}

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 8px !important;
        color: {text_primary} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
        outline: none !important;
    }}

    /* Radio buttons */
    .stRadio > div {{
        gap: 6px;
    }}

    /* Form styling */
    [data-testid="stForm"] {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.5rem;
    }}

    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #3B82F6, #6366F1) !important;
        border-radius: 4px !important;
    }}

    /* Expander */
    [data-testid="stExpander"] {{
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        background: {bg_card} !important;
    }}

    /* Tabs */
    [data-testid="stTabs"] [role="tab"] {{
        font-size: 14px !important;
        font-weight: 600 !important;
        color: {text_secondary} !important;
        padding: 8px 18px !important;
    }}

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        color: #3B82F6 !important;
        border-bottom-color: #3B82F6 !important;
    }}

    /* Alert boxes */
    [data-testid="stAlert"] {{
        border-radius: 10px !important;
        border: none !important;
    }}

    /* Spinner */
    [data-testid="stSpinner"] {{
        color: #3B82F6 !important;
    }}

    /* Streamlit markdown headings */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {text_primary} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Selectbox label */
    .stSelectbox label, .stTextInput label, .stTextArea label,
    .stRadio label, .stSlider label, .stNumberInput label {{
        color: {text_secondary} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }}

    /* Data table / dataframe */
    [data-testid="stDataFrame"] {{
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
    }}

    /* Leaderboard */
    .leaderboard-row {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: border-color 0.2s;
    }}

    .leaderboard-row:hover {{
        border-color: {border_hover};
    }}

    .rank-badge {{
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 14px;
        flex-shrink: 0;
    }}

    .rank-1 {{ background: linear-gradient(135deg, #F59E0B, #D97706); color: white; }}
    .rank-2 {{ background: linear-gradient(135deg, #94A3B8, #64748B); color: white; }}
    .rank-3 {{ background: linear-gradient(135deg, #D97706, #B45309); color: white; }}
    .rank-other {{ background: {bg_secondary}; color: {text_muted}; border: 1px solid {border_color}; }}

    /* ==========================================
       CV INTERVIEW SPECIFIC
    ========================================== */
    .cv-mode-banner {{
        background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(99,102,241,0.1));
        border: 1px solid rgba(139,92,246,0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }}

    .cv-mode-title {{
        font-size: 16px;
        font-weight: 700;
        color: #A78BFA;
        margin-bottom: 4px;
    }}

    .cv-skill-tag {{
        display: inline-block;
        background: rgba(59,130,246,0.12);
        color: #60A5FA;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px;
    }}

    /* Sidebar brand header */
    .sidebar-brand {{
        padding: 0 0 1rem 0;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid {border_color};
    }}

    .sidebar-logo {{
        font-size: 22px;
        font-weight: 800;
        color: {text_primary};
        letter-spacing: -0.5px;
    }}

    .sidebar-tagline {{
        font-size: 11px;
        color: {text_muted};
        margin-top: 2px;
    }}

    .nav-section-label {{
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: {text_muted};
        padding: 8px 14px 4px;
        display: block;
    }}

    .user-profile-strip {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 0.75rem;
    }}

    .user-name-sidebar {{
        font-size: 14px;
        font-weight: 600;
        color: {text_primary};
    }}

    .user-email-sidebar {{
        font-size: 11px;
        color: {text_muted};
    }}
    </style>
    """

    import streamlit as st
    st.markdown(css, unsafe_allow_html=True)
