from flask import Blueprint, render_template
from flask import current_app as app

# Blueprint Configuration
explanation_bp = Blueprint(
    'explanation_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@explanation_bp.route('/what-is-esa')
def explanation_esa():
    return render_template(
        "explanation_esa.html",
        title='What is ESA?'
    )


@explanation_bp.route('/what-is-ner')
def explanation_ner():
    return render_template(
        "explanation_ner.html",
        title='What is NER?'
    )


@explanation_bp.route('/how-do-recommendations-work')
def explanation_recommendation():
    return render_template(
        "explanation_recommendation.html",
        title="How do the recommendations work?"
    )
