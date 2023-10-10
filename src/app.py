"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [user.serialize() for user in users]

    response_body = {
        "users": results
    }

    return jsonify(response_body), 200
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    results = [character.serialize() for character in characters]
    return jsonify(results), 200
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)
    if character:
        return jsonify(character.serialize()), 200
@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    return jsonify(results), 200
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    user_id=get_users()
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorites_ready = [favorite.serialize() for favorite in favorites]

    return jsonify(favorites_ready), 200

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    user_id=get_users()
    add_favorite = Favorite(user_id=user_id, item_type='character', item_id=character_id)
    db.session.add(add_favorite)
    db.session.commit()
    
    return jsonify({"message": "Favorite character added"}), 201

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    user_id=get_users()
    favorite = Favorite.query.filter_by(user_id=user_id, item_type='character', item_id=character_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite character deleted successfully"}), 200 
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_to_favorite(planet_id):
    user_id=get_users()
    add_favorite = Favorite(user_id=user_id,item_type='planet', item_id=planet_id)
    db.session.add(add_favorite)
    db.session.commit() 
    return jsonify({"message": "Favorite planet added"}), 201
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id=get_users()
    favorite = Favorite.query.filter_by( user_id=user_id,item_type='planet', item_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite planet deleted successfully"}), 200
    


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
