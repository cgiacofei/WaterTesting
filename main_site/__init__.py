from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config.DevelopmentConfig')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from main_site.water_testing.models import User, TestSample, TestResult, Source, SourceType, Treatment
admin = Admin(app, name='Water Testing Administration', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Source, db.session))
admin.add_view(ModelView(SourceType, db.session))
admin.add_view(ModelView(Treatment, db.session))
admin.add_view(ModelView(TestSample, db.session))
admin.add_view(ModelView(TestResult, db.session))

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
from main_site.water_testing.views import mod_water as water_module

# Register blueprint(s)
app.register_blueprint(water_module)
# app.register_blueprint(xyz_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy
#db.create_all()
