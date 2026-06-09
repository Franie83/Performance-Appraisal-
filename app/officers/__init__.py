from flask import Blueprint

officers_bp = Blueprint('officers', __name__)

from app.officers import routes