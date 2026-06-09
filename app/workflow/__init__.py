from flask import Blueprint

workflow_bp = Blueprint('workflow', __name__)

from app.workflow import routes
