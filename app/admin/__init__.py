from flask import Blueprint, render_template 
from flask_login import login_required, current_user 
 
admin_bp = Blueprint('admin', __name__, url_prefix='/admin') 
 
@admin_bp.route('/test') 
@login_required 
def test(): 
    return render_template('admin/test.html') 
 
from app.admin import routes