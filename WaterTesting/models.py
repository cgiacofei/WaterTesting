import os
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from sqlalchemy.ext.hybrid import hybrid_property

from WaterTesting import app
db = SQLAlchemy(app)

# Base Model class to include boilerplate table fields
class BaseModel(db.Model)
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())


# Define the User data model. Make sure to add flask.ext.user UserMixin !!!
class User(BaseModel, UserMixin):

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')


# Table of water source type
# Public Utility, Shallow Well, etc...
class Type(BaseModel):
    name = db.Column(db.String(255), nullable=False, server_default='')


# Available water sources
# Richmond - Public Utility etc.
class Source(BaseModel):
    name = db.Column(db.String(255), nullable=False, server_default='')
    src_type = db.Column(db.Integer, db.ForeignKey('type.id'))
    samples = db.relationship('Test_Sample', backref="source", cascade="all, delete-orphan" , lazy='dynamic')

# Table for Many-To-Many relationship between test treatments and
# test samples.
test_treatment = db.Table(
    'test_treatment',
    db.Column('sample_id', db.Integer, db.ForeignKey('test_sample.id'), nullable=False),
    db.Column('treatment_id',db.Integer, db.ForeignKey('treatment.id'), nullable=False),
    db.PrimaryKeyConstraint('post_id', 'tags_id')
)


# Water sample treatment types
# Charcoal Filter, RO Filter etc.
class Treatment(BaseModel):
    name = db.Column(db.String(255), nullable=False, server_default='')


class Test_Sample(BaseModel):
    label = db.Column(db.String(12), nullable=True)
    source = db.Column(db.Integer, db.ForeignKey('source.id'))

    # Can have multiple test result per sample (in case of retest)
    results = db.relationship('Test_Result', backref="test_sample", cascade="all, delete-orphan" , lazy='dynamic')

    # Many-To-Many relationship
    treatments = db.relationship('Treatment', secondary=test_treatment, backref='test_sample' )


class Test_Result(BaseModel):
    sample = db.Column(db.Integer, db.ForeignKey('test_sample.id'))

    # Recorded Results
    total_hardness = db.Column(db.Float, nullable=False)
    ca_hardness = db.Column(db.Float, nullable=False)
    total_alkalinity = db.Column(db.Float, nullable=False)
    sulfate = db.Column(db.Float, nullable=False)
    chlorine = db.Column(db.Float, nullable=False)


    # Calculated Results
    @hybrid_property
    def mg_hardness(self):
        return self.total_hardness - self.ca_hardness

    @hybrid_property
    def res_alkalinity(self):
        return self.total_alkalinity - (self.ca_hardness / 3.5 + self.mg_hardness / 7)

    @hybrid_property
    def calcium(self):
        return self.ca_hardness * 0.4

    @hybrid_property
    def magnesium(self):
        return self.mg_hardness * 0.25

    @hybrid_property
    def bicarbonate(self):
        return self.total_alkalinity * 1.22

    @hybrid_property
    def sulfate_chlorine_ratio(self):
        return self.sulfate / self.chlorine

    @hybrid_property
    def balance(self):
        from bisect import bisect

        r_lkup = {
            0: 'Too Malty',
            0.4: 'Very Malty',
            .6: 'Malty',
            .8: 'Balanced',
            1.5: 'Little Bitter',
            2.0: 'More Bitter',
            4.0: 'Extra Bitter',
            6.0: 'Quite Bitter',
            8.0: 'Very Bitter',
            9.0: 'Too Bitter'
        }

        r = self.sulfate_chlorine_ratio

        # min/max functions support custom keys to compare list items with.
        # In this case the key is the difference between each list value and
        # the keys in the r_lkup dictionary.
        return r_lkup[min(r_lkup.keys(), key=lambda x: abs(x - r))]

