"""Custom CSS styles for the Streamlit application."""


def get_custom_css() -> str:
    """
    Get the custom CSS styles for the application.

    Returns:
        CSS string to be injected via st.markdown
    """
    return """
    <style>
    /* ========================================
       GLOBAL STYLES
       ======================================== */

    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Main app background */
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Remove default padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* ========================================
       TYPOGRAPHY
       ======================================== */

    h1 {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }

    h3 {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-bottom: 0.5rem !important;
    }

    p {
        color: #64748B !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }

    /* ========================================
       HEADER / HERO SECTION
       ======================================== */

    .hero-container {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(79, 70, 229, 0.2);
    }

    .hero-title {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }

    .hero-subtitle {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.125rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* ========================================
       STEP INDICATOR
       ======================================== */

    .step-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem 0;
    }

    .step-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }

    .step-item:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 15px;
        right: -50%;
        width: 100%;
        height: 2px;
        background-color: #E2E8F0;
        z-index: 0;
    }

    .step-item.completed:not(:last-child)::after {
        background-color: #10B981;
    }

    .step-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 14px;
        z-index: 1;
        transition: all 0.3s ease;
    }

    .step-circle.pending {
        background-color: #F1F5F9;
        color: #94A3B8;
        border: 2px solid #E2E8F0;
    }

    .step-circle.current {
        background-color: #4F46E5;
        color: white;
        border: 2px solid #4F46E5;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.2);
        animation: pulse 2s infinite;
    }

    .step-circle.completed {
        background-color: #10B981;
        color: white;
        border: 2px solid #10B981;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.2); }
        50% { box-shadow: 0 0 0 8px rgba(79, 70, 229, 0.1); }
        100% { box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.2); }
    }

    .step-label {
        margin-top: 8px;
        font-size: 12px;
        font-weight: 500;
        color: #64748B;
        text-align: center;
    }

    .step-item.current .step-label {
        color: #4F46E5;
        font-weight: 600;
    }

    .step-item.completed .step-label {
        color: #10B981;
    }

    /* ========================================
       CARDS
       ======================================== */

    .stCard {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stCard:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #E2E8F0;
    }

    .card-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        font-size: 1.25rem;
    }

    .card-title {
        font-weight: 600;
        font-size: 1.125rem;
        color: #1E293B;
        margin: 0;
    }

    .card-subtitle {
        font-size: 0.875rem;
        color: #64748B;
        margin: 0;
    }

    /* ========================================
       BUTTONS
       ======================================== */

    .stButton > button {
        background-color: #4F46E5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background-color: #4338CA !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    .stButton > button:disabled {
        background-color: #CBD5E1 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Secondary button style */
    .secondary-button > button {
        background-color: white !important;
        color: #475569 !important;
        border: 1px solid #E2E8F0 !important;
    }

    .secondary-button > button:hover {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        border-color: #CBD5E1 !important;
    }

    /* Danger button style */
    .danger-button > button {
        background-color: #EF4444 !important;
    }

    .danger-button > button:hover {
        background-color: #DC2626 !important;
    }

    /* ========================================
       FORM INPUTS
       ======================================== */

    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #1E293B !important;
        background-color: white !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #94A3B8 !important;
    }

    /* Valid/Invalid states */
    .input-valid > div > div > input {
        border-color: #10B981 !important;
        background-color: #F0FDF4 !important;
    }

    .input-invalid > div > div > input {
        border-color: #EF4444 !important;
        background-color: #FEF2F2 !important;
    }

    /* ========================================
       FILE UPLOADER
       ======================================== */

    .stFileUploader > div {
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        background-color: #F8FAFC !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }

    .stFileUploader > div:hover {
        border-color: #4F46E5 !important;
        background-color: #F5F3FF !important;
    }

    .stFileUploader > div > div > div > div {
        color: #64748B !important;
        font-size: 0.875rem !important;
    }

    .stFileUploader > div > div > small {
        color: #94A3B8 !important;
        font-size: 0.75rem !important;
    }

    /* ========================================
       ALERTS / NOTIFICATIONS
       ======================================== */

    .alert {
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid transparent;
    }

    .alert-success {
        background-color: #F0FDF4;
        border-color: #10B981;
        color: #065F46;
    }

    .alert-error {
        background-color: #FEF2F2;
        border-color: #EF4444;
        color: #991B1B;
    }

    .alert-warning {
        background-color: #FFFBEB;
        border-color: #F59E0B;
        color: #92400E;
    }

    .alert-info {
        background-color: #EFF6FF;
        border-color: #3B82F6;
        color: #1E40AF;
    }

    /* ========================================
       UTILITY CLASSES
       ======================================== */

    .text-center {
        text-align: center !important;
    }

    .text-left {
        text-align: left !important;
    }

    .text-right {
        text-align: right !important;
    }

    .mt-1 { margin-top: 0.25rem !important; }
    .mt-2 { margin-top: 0.5rem !important; }
    .mt-3 { margin-top: 1rem !important; }
    .mt-4 { margin-top: 1.5rem !important; }
    .mt-5 { margin-top: 2rem !important; }

    .mb-1 { margin-bottom: 0.25rem !important; }
    .mb-2 { margin-bottom: 0.5rem !important; }
    .mb-3 { margin-bottom: 1rem !important; }
    .mb-4 { margin-bottom: 1.5rem !important; }
    .mb-5 { margin-bottom: 2rem !important; }

    .p-1 { padding: 0.25rem !important; }
    .p-2 { padding: 0.5rem !important; }
    .p-3 { padding: 1rem !important; }
    .p-4 { padding: 1.5rem !important; }
    .p-5 { padding: 2rem !important; }

    /* Hide Streamlit default elements */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .stDeployButton {
        display: none;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }

    </style>
    """
