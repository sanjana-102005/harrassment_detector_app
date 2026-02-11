"""
Utility functions for the harassment detection app.
"""

def format_confidence_score(score: float) -> str:
    """Format confidence score as percentage."""
    return f"{score * 100:.1f}%"

def get_severity_color(severity: str) -> str:
    """Get color code based on severity level."""
    colors = {
        'Critical': '#8B0000',  # Dark red
        'High': '#FF4444',      # Red
        'Medium': '#FFA500',    # Orange
        'Low': '#FFD700',       # Gold
        'None': '#90EE90'       # Light green
    }
    return colors.get(severity, '#CCCCCC')

def sanitize_input(text: str) -> str:
    """Basic sanitization of user input."""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Limit length
    return text[:5000]

def validate_incident_text(text: str) -> tuple[bool, str]:
    """
    Validate incident description.
    Returns (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Please provide a description of the incident."
    
    if len(text.strip()) < 10:
        return False, "Please provide more details about the incident (at least 10 characters)."
    
    if len(text) > 5000:
        return False, "Description is too long. Please limit to 5000 characters."
    
    return True, ""
