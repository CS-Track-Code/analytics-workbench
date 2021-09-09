from flask import Blueprint, render_template, redirect, url_for
from application.cstrack_dash import dash_cs as dcs
from flask import current_app as app
import requests as py_requests

import config

# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@home_bp.route('/')
def startpage():
    return render_template(
        "startpage.html",
        title='Analytics Workbench'
    )


@home_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Standard `contact` form."""
    return render_template(
        "contact.html",
        title="Contact us",
    )


@home_bp.route('/legal-notice')
def legal_notice():
    return render_template(
        "impressum-legal.html",
        title="Legal Notice"
    )


@home_bp.route('/get-project-names')
def get_project_names():
    url = config.middleware + "db/project-names"
    data = {}

    data_response = py_requests.get(url, data=data)
    content = data_response.content

    return content


@home_bp.route('/get-tba-projects')
def get_tba_project_names():
    url = config.middleware + "db/tba-project-names"
    data = {}

    data_response = py_requests.get(url, data=data)
    content = data_response.content

    return content


@home_bp.route('/load_dashapp')
def load_dashapp():
    from flask import current_app as app

    app, server = dcs.create_dashboard(app)
    return redirect("/dashapp")
