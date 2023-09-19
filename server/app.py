#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict(rules=('-planets', '-missions'))
                    for scientist in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        try:
            new_scientist = Scientist(
                name=request.json['name'],
                field_of_study=request.json['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()

            return new_scientist.to_dict(rules=('-planets', '-missions')), 201
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
    
api.add_resource(Scientists, '/scientists')

class Planets(Resource):

    def get(self):
        planets = [planet.to_dict(rules=('-scientists', '-missions'))
                for planet in Planet.query.all()]
        return make_response(planets, 200)

api.add_resource(Planets, '/planets')

class Missions(Resource):

    def post(self):
        try:
            new_mission = Mission(
                name=request.json['name'],
                planet_id=request.json['planet_id'],
                scientist_id=request.json['scientist_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Missions, '/missions')

class ScientistByID(Resource):

    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        return make_response(scientist.to_dict(), 200)
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        data = request.get_json()
        try:
            setattr(scientist, 'name', data['name'])
            setattr(scientist, 'field_of_study', data['field_of_study'])
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(rules=('-planets', '-missions')), 202
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        elif scientist:
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)
    
api.add_resource(ScientistByID, '/scientists/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
