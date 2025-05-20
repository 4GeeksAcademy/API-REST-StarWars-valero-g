"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from sqlalchemy import and_, delete, null, select, or_
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, favoritos
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


# GET de USER
@app.route('/users', methods=['GET'])
def get_users():
    try:
        all_users =  db.session.execute(select(User)).scalars().all()
        # Validacion
        if all_users == None:
            return {"message" : "No user can be found"}, 404
        # Respuesta
        all_users = list(map(lambda x: x.serialize(), all_users))
        return jsonify(all_users), 200
    except:
        return {"message":"Error: users cannot be found"}, 404

@app.route('/users/<int:user_id>', methods = ['GET'])
def get_users_by_id(user_id):
    try:
        user =  db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        # Validacion
        if user == None:
            return {"message" : f"User ID {user_id} cannot be found"}, 400
        # Respuesta
        return jsonify(user.serialize()), 200
    except:
        return {"message": f"Error when retrieving information of user {user_id}"}, 400

# GET de CHARACTERS

@app.route('/people', methods= ['GET'])
def get_characters():
    try:
        all_people =  db.session.execute(select(Characters)).scalars().all()
        # Validacion
        if all_people == None:
            return {"message" : "No character can be found"}, 404
        # Respuesta
        all_people = list(map(lambda x: x.serialize(), all_people))
        return jsonify(all_people), 200
    except:
        return {"message":"Error: characters cannot be found"}, 404

@app.route('/people/<int:people_id>', methods = ['GET'])
def get_characters_by_id(people_id):
    try:
        people =  db.session.execute(select(Characters).where(Characters.id == people_id)).scalar_one_or_none()
        # Validacion
        if people == None:
            return {"message" : f"Character ID {people_id} cannot be found"}, 400
        # Respuesta
        return jsonify(people.serialize()), 200
    except:
        return {"message": f"Error when retrieving information of character {people_id}"}, 400


# PUT de characters
@app.route('/people/<int:people_id>', methods = ['PUT'])
def put_character_by_id(people_id):
    try:
        body= request.get_json(silent = True)
        print(body)
        people = db.session.execute(select(Characters).where(Characters.id == people_id)).scalar_one_or_none()
        # Validación de people_id
        if people == None:
            return {"message" : f"Character ID {people_id} cannot be found"}, 404  
        # Validación del body
        if "name" not in body.keys() or "age" not in body.keys():
            return {"message" : f"Wrong request"}, 400 
        # Update de la tabla
        update_people = db.session.get(Characters, people_id) 
        update_people.name = body["name"]
        update_people.age = body["age"]
        db.session.commit()
        # Retornamos el personaje actualizado
        people = db.session.execute(select(Characters).where(Characters.id == people_id)).scalar_one_or_none()
        return people.serialize(),200

    except Exception as e:
        print("Error:", e)
        return {"message": "Error updating character"}, 500
    
# DELETE de characters 
@app.route('/people/<int:people_id>', methods = ['DELETE'])
def delete_people_by_id(people_id):
    try:
        #people = db.session.execute(select(Characters).where(Characters.id == people_id)).scalar_one_or_none()
        character = db.session.get(Characters, people_id)
        # Validación de people_id
        if character == None:
            return {"message" : f"Character ID {people_id} cannot be found"}, 404   
        db.session.delete(character)
        db.session.commit()
        return {"message": f"Character {people_id} deleted"}

    except Exception as e:
        print("Error:", e)
        return {"message": "Error deleting character"}, 500
    

# GET de PLANETS
@app.route('/planets', methods= ['GET'])
def get_planets():
    try:
        all_planets =  db.session.execute(select(Planets)).scalars().all()
        # Validacion
        if all_planets == None:
            return {"message" : "No planet can be found"}, 404
        # Respuesta
        all_planets = list(map(lambda x: x.serialize(), all_planets))
        return jsonify(all_planets), 200
    except:
        return {"message":"Error: planets cannot be found"}, 404
    

@app.route('/planets/<int:planets_id>', methods = ['GET'])
def get_planets_by_id(planets_id):
    try:
        planet =  db.session.execute(select(Planets).where(Planets.id == planets_id)).scalar_one_or_none()
        # Validacion
        if planet == None:
            return {"message" : f"Planet ID {planets_id} cannot be found"}, 400
        # Respuesta
        return jsonify(planet.serialize()), 200
    except:
        return {"message": f"Error when retrieving information of planet {planets_id}"}, 400
    

# PUT de Planets
@app.route('/planet/<int:planet_id>', methods = ['PUT'])
def put_planet_by_id(planet_id):
    try:
        body= request.get_json(silent = True)
        planet = db.session.execute(select(Planets).where(Planets.id == planet_id)).scalar_one_or_none()
        # Validación de planet_id
        if planet == None:
            return {"message" : f"Planet ID {planet_id} cannot be found"}, 404  
        # Validación del body
        if "name" not in body.keys() or "size" not in body.keys() or "gravity" not in body.keys():
            return {"message" : f"Wrong request"}, 400 
        # Update de la tabla
        update_planet = db.session.get(Planets, planet_id) 
        update_planet.name = body["name"]
        update_planet.size = body["size"]
        update_planet.gravity = body["gravity"]
        db.session.commit()
        # Retornamos el planeta actualizado
        planet = db.session.execute(select(Planets).where(Planets.id == planet_id)).scalar_one_or_none()
        return planet.serialize(),200

    except Exception as e:
        print("Error:", e)
        return {"message": "Error updating planet"}, 500
    
# DELETE de planets 
@app.route('/planet/<int:planet_id>', methods = ['DELETE'])
def delete_planet_by_id(planet_id):
    try:
        #people = db.session.execute(select(Characters).where(Characters.id == people_id)).scalar_one_or_none()
        planet = db.session.get(Planets, planet_id)
        # Validación de people_id
        if planet == None:
            return {"message" : f"Character ID {planet_id} cannot be found"}, 404   
        db.session.delete(planet)
        db.session.commit()
        return {"message": f"Planet {planet_id} deleted"}

    except Exception as e:
        print("Error:", e)
        return {"message": "Error deleting planet"}, 500





# GET de favourites
@app.route('/users/<int:id_user>/favorites', methods = ['GET'])
def get_favorites_by_id(id_user):
    try:
        # Validar la existencia de usuario
        user =  db.session.execute(select(User).where(User.id == id_user)).scalar_one_or_none()
        if user is None:
            return {"message":f"User {id_user} cannot be found"}, 404
        favorite_planets = []
        favorite_characters = []
        # Buscar planetas favoritos del usuario y los añadimos al arreglo de planetas favoritos
        for favorite_planet in user.favourites_planet:
            if favorite_planet is not None: #TBC, mejor imprimir y ver qué devuelve
                favorite_planets.append(favorite_planet.serialize())

        # Buscar personajes favoritos del usuario y los añadimos al arreglo de personajes favoritos
        for favorite_character in user.favourites_character:
            if favorite_character is not None:
                favorite_characters.append(favorite_character.serialize())

        return {"User_id":id_user,"favourite_planets": favorite_planets, "favorite_people": favorite_characters }, 200
    except Exception as e:
        print("Error:", e)
        return {"message": "Error retrieving favorites"}, 500




# POST de favorites
@app.route('/favorite/planet/<int:planet_id>', methods= ['POST'])
def add_favorite_planet(planet_id):
    try:
        request_body = request.get_json(silent = True)
        print(request_body["user_id"])
        # validacion de request
        if request_body is None:
            return {"message": "Wrong request"}, 400
        if "user_id" not in request_body:
            return {"message": "Wrong request"}, 400
        # Validación de la existencia de User ID
        user = db.session.execute(select(User).where(User.id == request_body["user_id"])).scalar_one_or_none()

        if user is None:
            return {"message": "User cannot be found"}, 404
        # Validación de la existencia de Planeta
        planet = db.session.execute(select(Planets).where(Planets.id == planet_id)).scalar_one_or_none()
        if planet is None:
            return {"message": "Planet cannot be found"}, 404
        # Validación de no existencia del favorito (favoritos es tabla, no clase)
        test_favorite_planet = db.session.execute(select(favoritos).where(and_(favoritos.c.user_id == request_body["user_id"], favoritos.c.planet_id == planet_id))).first()
        if test_favorite_planet != None:
            return {"message": f"Planet {planet_id} is already a favorite planet of user {request_body["user_id"]}"}, 400
        # Agregamos favorito (favoritos es tabla, no clase)
        #db.session.execute(favoritos.insert().values(user_id=request_body["user_id"], planet_id=planet_id, character_id=None))
        stmt = favoritos.insert().values(user_id=request_body["user_id"],planet_id=planet_id,character_id=None)
        db.session.execute(stmt)
        db.session.commit()
        return {"message": f"Favourite planet {planet_id} added to favorites of user"}, 200
    except Exception as e:
        print("Error:", e)
        return {"message": f"Error: cannot add planet {planet_id} to user's favorites"}, 500

@app.route('/favorite/people/<int:people_id>', methods= ['POST'])
def add_favorite_people(people_id):
    try:
        request_body = request.get_json(silent = True)
        # validacion de request
        if request_body is None:
            return {"message": "Wrong request"}, 400
        if "user_id" not in request_body:
            return {"message": "Wrong request"}, 400
        # Validación de la existencia de User ID
        user = db.session.execute(select(User).where(User.id == request_body["user_id"])).scalar_one_or_none()
        if user is None:
            return {"message": "User cannot be found"}, 404
        # Validación de la existencia de Personaje
        people = db.session.execute(select(Characters).where(Characters.id == people_id)).scalar_one_or_none()
        if people is None:
            return {"message": "Character cannot be found"}, 404
        # Validación de no existencia del favorito (favoritos es tabla, no clase)
        test_favorite_people = db.session.execute(select(favoritos).where(and_(favoritos.c.user_id == request_body["user_id"], favoritos.c.character_id == people_id))).first()
        if test_favorite_people!= None:
            return {"message": f"Character {people_id} is already a favorite character of user {request_body["user_id"]}"}, 400
        # Agregamos favorito (favoritos es tabla, no clase)
        stmt = favoritos.insert().values(user_id=request_body["user_id"],character_id=people_id,planet_id=None)
        db.session.execute(stmt)
        db.session.commit()
        return {"message": f"Favourite character {people_id} added to favorites of user"}, 200
    except Exception as e:
        print("Error:", e)
        return {"message": f"Error: cannot add character {people_id} to user's favorites"}, 500



@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    try:
        # Buscar el registro favorito
        result = db.session.execute(select(favoritos).where(and_(favoritos.c.user_id == user_id,favoritos.c.planet_id == planet_id))).first()

        if result is None:
            return {
                "message": f"Planet {planet_id} is not a favorite planet of user {user_id}"
            }, 404

        favorite_id = result.id

        # Borrar el favorito
        stmt = delete(favoritos).where(favoritos.c.id == favorite_id)
        db.session.execute(stmt)
        db.session.commit()

        return {"message": f"Planet {planet_id} removed from favorites of user {user_id}"}, 200

    except Exception as e:
        print("Error:", e)
        return {"message": f"Error: cannot delete {planet_id} from user's favorites"}, 500
    
@app.route('/favorite/user/<int:user_id>/people/<int:people_id>', methods= ['DELETE'])
def delete_favorite_people(user_id, people_id):
    try:
        # Buscar el registro favorito
        result = db.session.execute(select(favoritos).where(and_(favoritos.c.user_id == user_id,favoritos.c.character_id == people_id))).first()

        if result is None:
            return {
                "message": f"Character {people_id} is not a favorite planet of user {user_id}"
            }, 404

        favorite_id = result.id

        # Borrar el favorito
        stmt = delete(favoritos).where(favoritos.c.id == favorite_id)
        db.session.execute(stmt)
        db.session.commit()

        return {"message": f"Character {people_id} removed from favorites of user {user_id}"}, 200

    except Exception as e:
        print("Error:", e)
        return {"message": f"Error: cannot delete {people_id} from user's favorites"}, 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)