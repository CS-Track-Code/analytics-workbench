from flask import Blueprint, render_template
from flask import current_app as app

# Blueprint Configuration
error_bp = Blueprint(
    'error_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@error_bp.app_errorhandler(404)
def er404(error):
    return render_template(
        'error404.html',
        title="Page not found"
    )
