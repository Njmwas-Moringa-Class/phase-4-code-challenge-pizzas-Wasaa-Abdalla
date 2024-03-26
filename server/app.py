from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
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


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
    response = make_response(jsonify(restaurants), 200)
    return response


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurantById(id):
    restautant = Restaurant.query.filter_by(id=id).first()
    if not restautant:
        return jsonify({"error": "Restaurant not found"}), 404
    restaurarnt_dict = restautant.to_dict()
    response = make_response(restaurarnt_dict, 200)
    return response


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurantById(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    if db.session.dirty:
        db.session.commit()
        return '', 204
    else:
        return '', 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    response = make_response(pizzas, 200)
    return response


@app.route("/restaurant_pizzas", methods=["POST"])
def post_restaurant_pizza():

    data = request.json

    required_fields = ["restaurant_id", "pizza_id", "price"]
    if not all(key in data for key in required_fields):
        return jsonify(errors=["Missing required fields"]), 400

    restaurant_id = data["restaurant_id"]
    pizza_id = data["pizza_id"]
    price = data["price"]

    if not 1 <= price <= 30:
        return jsonify({"errors": ["validation errors"]}), 400

    restaurant_pizza = RestaurantPizza(
        restaurant_id=restaurant_id, pizza_id=pizza_id, price=price
    )

    db.session.add(restaurant_pizza)
    db.session.commit()

    pizza = Pizza.query.get_or_404(pizza_id)
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    response_data = {
        "id": restaurant_pizza.id,
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
        },
        "pizza": {"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients},
        "pizza_id": pizza_id,
        "price": price,
        "restaurant_id": restaurant_id,
    }

    return jsonify(response_data), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
