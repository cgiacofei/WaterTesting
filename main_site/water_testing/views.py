import os
from flask import render_template, Blueprint

# Import the database object from the main app module
from main_site import db

# Import module forms
from main_site.water_testing.forms import LoginForm

# Import module models (i.e. User)
from main_site.water_testing.models import User, TestSample, Source

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_water = Blueprint('water', __name__, url_prefix='/water')

@mod_water.route('/')
def index():
    recent = None
    return render_template('water/index.html', recent=recent )


# Setting route to test result
@mod_water.route('/result/<int:sample_id>/')
def result(sample_id):
    reports = Test_Sample.query.get_or_404(sample_id).results
    return render_template('water/report.html', reports=reports )


# Setting route to test result
@mod_water.route('/result/index/')
def result_index():
    return 'ToDo'

# Setting route to location summary page with plots
@mod_water.route('/location/<location>/')
def summary(location):
    samples = Source.query.get(location).samples

    summary = build_source_summary(samples, location)

    locations = Source.query.all()
    
    return render_template('water/location.html', summary=summary, pages=locations)
