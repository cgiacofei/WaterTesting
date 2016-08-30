import os
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    FREEZER_REMOVE_EXTRA_FILES = True

    FREEZER_DESTINATION = os.path.join(ROOT_DIR, 'html')
    FREEZER_RELATIVE_URLS = True

class ProductionConfig(BaseConfig):


class DevelopmentConfig(BaseConfig):
    DATA_FILE = os.path.join(ROOT_DIR, 'WaterTesting', 'data.csv')
    DEBUG = True
    TESTING = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
