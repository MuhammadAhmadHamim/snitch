import streamlit as st

PALETTE = {
    "bg": "#141414",
    "surface": "#1F1F1F",
    "accent": "#D7263D",
    "success": "#2ECC71",
    "alert": "#D7263D",
    "text": "#F2F2F2",
    "text_muted": "#9A9A9A",
}

def inject_theme() -> None:
    """Injects fonts and custom CSS for the Vault theme. Call once per page."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

        h1, h2, h3 {
            font-family: 'Oswald', sans-serif;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }

        p, span, label, div {
            font-family: 'Inter', sans-serif;
        }

        /* --- Metrics --- */
        [data-testid="stMetric"] {
            background-color: #1F1F1F;
            border: 1px solid #2A2A2A;
            border-radius: 6px;
            padding: 0.75rem;
        }

        [data-testid="stMetricValue"] {
            font-family: 'Oswald', sans-serif;
            font-weight: 600;
        }

        [data-testid="stMetricLabel"] {
            color: #9A9A9A;
            font-size: 0.85rem;
        }

        /* --- Containers / forms --- */
        div[data-testid="stForm"],
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #1F1F1F;
            border: 1px solid #2A2A2A;
            border-radius: 6px;
        }

        /* --- Buttons --- */
        .stButton button {
            background-color: #D7263D;
            color: #F2F2F2;
            border: none;
            border-radius: 4px;
        }

        .stButton button:hover {
            background-color: #B81F33;
            color: #F2F2F2;
        }

        /* --- Vault status tags --- */
        .vault-tag {
            display: inline-block;
            font-family: 'Oswald', sans-serif;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 0.2rem 0.6rem;
            border-radius: 3px;
            border: 1px solid currentColor;
        }

        /* --- Always-visible input borders --- */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] > div,
        [data-testid="stTimeInput"] > div,
        [data-testid="stSelectbox"] > div {
            border: 1px solid #2A2A2A !important;
            border-radius: 4px !important;
        }

        .vault-tag-ok { color: #2ECC71; }
        .vault-tag-warning { color: #E8A33D; }
        .vault-tag-over { color: #D7263D; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def status_tag(status: str) -> str:
    """Returns an HTML snippet for a small status badge (OPERATION-style tag)."""
    labels = {
        "ok": ("vault-tag-ok", "OPERATION SECURE"),
        "warning": ("vault-tag-warning", "OPERATION AT RISK"),
        "over": ("vault-tag-over", "OPERATION COMPROMISED"),
    }
    css_class, label = labels.get(status, ("vault-tag-ok", "UNKNOWN"))
    return f'<span class="vault-tag {css_class}">{label}</span>'