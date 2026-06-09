from flask import Blueprint

assessments_bp = Blueprint('assessments', __name__)

from app.assessments import routes