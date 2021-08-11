from flask import Blueprint, request, abort
from werkzeug.wrappers import Response
import requests as py_requests
import json

from text_extraction import mercury_web_parser as mercury
import config

# Blueprint Configuration
mercury_bp = Blueprint(
    'mercury_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@mercury_bp.route('/mercury/get_project_text', methods=['POST'])
def get_project_text():
    name = request.form["name"]
    project_url = request.form['link']
    if project_url is not None:
        url_data = config.backend_data + "data/project-description"
        data = {
            "name": name,
            "link": project_url
        }
        data_response = py_requests.post(url_data, data=data)
        if data_response.status_code == 200:
            content = json.loads(data_response.content)
            website_text = content["project_description"]
        else:
            website_text = None
        if website_text is None:
            print(project_url)
            website_text = mercury.extract_text(config.backend_mercury, project_url)

            url_data = config.backend_data + "data/save-new-project"
            data = {
                "name": name,
                "link": project_url,
                "description": website_text
            }
            data_response = py_requests.post(url_data, data=data)

        header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
        response = Response(website_text, status=200, headers=header)
        return response
    else:
        abort(404)
