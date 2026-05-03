"""Step indicator component for showing progress through the upload flow."""
import streamlit as st
from typing import List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException


logger = CustomLogger(log_dir="logs").get_logger(__name__)

STEPS = ["Start", "VTT Files", "Code Files", "GitHub", "Review", "Done"]


def render_step_indicator(current_step: int, steps: List[str] = None) -> None:
    """
    Render the step indicator component.

    Args:
        current_step: Current step index (0-based)
        steps: List of step labels. Defaults to STEPS.
    """
    try:
        if steps is None:
            steps = STEPS

        logger.debug("Rendering step indicator", current_step=current_step, total_steps=len(steps))

        # Create HTML for step indicator
        html = '<div class="step-container">'

        for i, step in enumerate(steps):
            # Determine step state
            if i < current_step:
                state = "completed"
                icon = "✓"
            elif i == current_step:
                state = "current"
                icon = str(i + 1)
            else:
                state = "pending"
                icon = str(i + 1)

            html += f'''
                <div class="step-item {state}">
                    <div class="step-circle {state}">{icon}</div>
                    <div class="step-label">{step}</div>
                </div>
            '''

        html += '</div>'

        # Render the HTML
        st.markdown(html, unsafe_allow_html=True)

        # Add spacing
        st.markdown("<br/>", unsafe_allow_html=True)

        logger.debug("Step indicator rendered successfully")

    except Exception as e:
        logger.error("Failed to render step indicator", current_step=current_step, error=str(e))
        raise RagAppException(f"Failed to render step indicator: {str(e)}", e)


def get_step_progress(current_step: int, total_steps: int = None) -> float:
    """
    Get the progress percentage for the current step.

    Args:
        current_step: Current step index (0-based)
        total_steps: Total number of steps. Defaults to len(STEPS).

    Returns:
        Progress percentage (0-100)
    """
    if total_steps is None:
        total_steps = len(STEPS)

    progress = (current_step / (total_steps - 1)) * 100 if total_steps > 1 else 0
    return min(100, max(0, progress))
