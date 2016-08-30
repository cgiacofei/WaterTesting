
import os
from flask import render_template
from slugify import Slugify

from WaterTesting import app
from models import Test_Sample, Source


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SLUG = Slugify(to_lower=True)

@app.route('/')
def index():
    recent = None
    return render_template('index.html', recent=recent )


# Setting route to test result
@app.route('/result/<int:sample_id>/')
def result(sample_id):
    reports = Test_Sample.query.get_or_404(sample_id).results
    return render_template('report.html', reports=reports )


# Setting route to test result
@app.route('/result/index/')
def result_index():
    return 'ToDo'

# Setting route to location summary page with plots
@app.route('/location/<location>/')
def summary(location):
    samples = Source.query.get(location).samples

    summary = build_source_summary(samples, location)

    locations = Source.query.all()
    
    return render_template('location.html', summary=summary, pages=locations)
