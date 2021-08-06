from flask import Blueprint, render_template, request
from flask import current_app as app
from werkzeug.wrappers import BaseResponse
import requests as py_requests
import json

import config

# Blueprint Configuration
testing_bp = Blueprint(
    'testing_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@testing_bp.route('/testing/dashboard')
def test_dashboard():
    return render_template(
        "dashboard_test.html",
        title="Explore Data - Dashboard"
    )
