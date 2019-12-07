"""
Db Conenctor class.
"""
from flask import Flask
from flask_pymongo import PyMongo

class DbConnector:
    """
    This class implements pseudo singleton pattern
    If you try to create a second object of this type
    the constructor will throw an error
    """
    __instance = None
    mongo = None

    def __init__(self):
        if DbConnector.__instance is not None:
            raise Exception('Can not create another instance of this')
        else:
            app = Flask(__name__)
            app.config.from_envvar("SETTINGS")
            app.config["MONGO_URI"] = app.config.get("MONGO_URI")
            self.mongo = PyMongo(app)
            DbConnector.__instance = self

    @staticmethod
    def get_connection():
        """
        Static method to get the mongo connection object
        """
        if DbConnector.__instance is None:
            DbConnector()
        return DbConnector.__instance.mongo
        