from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)
    missions = db.relationship(
        'Mission', cascade='all,delete', backref='planet')
    scientists = association_proxy('missions', 'scientist')

    serialize_rules = ('-missions.planet', '-scientists.planet')


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)
    missions = db.relationship(
        'Mission',cascade='all,delete',backref='scientist')
    planets = association_proxy('missions', 'planet')

    serialize_rules = ('-missions.scientist', '-planet.scientists')

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('Name property required')
        return name
    
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if not field_of_study:
            raise ValueError('Field of study property required')
        return field_of_study

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))

    serialize_rules = ('-scientist.missions', '-planet.missions')

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('Name property required')
        return name

    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if not scientist_id:
            raise ValueError('Scientist ID property required')
        return scientist_id

    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if not planet_id:
            raise ValueError('Planet ID property required')
        return planet_id


# add any models you may need.
