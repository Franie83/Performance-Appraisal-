from flask import Blueprint

quarterly_bp = Blueprint('quarterly', __name__, url_prefix='/quarterly')

# Import routes at the bottom to avoid circular imports
from app.quarterly import routes