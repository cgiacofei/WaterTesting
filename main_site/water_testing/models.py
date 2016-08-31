import os
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from main_site import db

now = datetime.datetime.now

# Base Model class to include boilerplate table fields
class BaseModel(object):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime(), default=now())
    modified = db.Column(db.DateTime(), default=now())


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())

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
class SourceType(db.Model, BaseModel):

    name = db.Column(db.String(255), nullable=False, server_default='')

    def __str__(self):
        return self.name


# Available water sources
# Richmond - Public Utility etc.
class Source(db.Model, BaseModel):

    name = db.Column(db.String(255), nullable=False, server_default='')

    type_id = db.Column(db.Integer, db.ForeignKey('source_type.id'))
    src_type = db.relationship("SourceType", backref="sources")

    def __str__(self):
        return '{} [{}]'.format(self.name, self.src_type)


# Table for Many-To-Many relationship between test treatments and
# test samples.
test_treatment = db.Table(
    'test_treatment',
    db.Column('sample_id', db.Integer, db.ForeignKey('test_sample.id'), nullable=False),
    db.Column('treatment_id',db.Integer, db.ForeignKey('treatment.id'), nullable=False),
    db.PrimaryKeyConstraint('sample_id', 'treatment_id')
)


# Water sample treatment types
# Charcoal Filter, RO Filter etc.
class Treatment(db.Model, BaseModel):

    name = db.Column(db.String(255), nullable=False, server_default='')

    def __str__(self):
        return self.name


class TestSample(db.Model, BaseModel):
    
    sample_date = db.Column(db.DateTime())
    label = db.Column(db.String(12), nullable=True)
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))
    source = db.relationship("Source", backref="samples")
    # Can have multiple test result per sample (in case of retest)
    results = db.relationship('TestResult', backref="test_sample", cascade="all, delete-orphan" , lazy='dynamic')

    # Many-To-Many relationship
    treatments = db.relationship('Treatment', secondary=test_treatment, backref='test_sample' )


    def __str__(self):
        return '{} {}'.format(self.sample_date, self.source_id)


class TestResult(db.Model, BaseModel):

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

