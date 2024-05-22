#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from models import Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Restaurants(Resource):
    def get(self):
        return make_response(jsonify([restaurant.to_dict() for restaurant in Restaurant.query.all()]), 200)
    
class RestaurantsById(Resource):
    def get(self, id):
        restaurant = db.session.query(Restaurant).get(id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        return make_response(jsonify(restaurant.to_dict(rules=("restaurant_pizzas",))), 200)

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

        RestaurantPizza.query.filter_by(restaurant_id=id).delete()

        db.session.delete(restaurant)
        db.session.commit()

        return make_response("", 204)

    
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizza_data = [{"id": pizza.id, "ingredients": pizza.ingredients, "name": pizza.name} for pizza in pizzas]
        return make_response(jsonify(pizza_data), 200)
    
class RestaurantPizzas(Resource):
    def post(self):
        restaurantPizza_data = request.get_json()
        try:
            price = restaurantPizza_data.get('price')
            pizza_id = restaurantPizza_data.get('pizza_id')
            restaurant_id = restaurantPizza_data.get('restaurant_id')
            restaurantPizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurantPizza)
            db.session.commit()
            return make_response(jsonify(restaurantPizza.to_dict()), 201)
        except Exception as e:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Pizzas, "/pizzas")
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantsById, "/restaurants/<int:id>")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")



@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)

