import os, pymongo, data_functions

from flask import Flask, render_template, url_for, request, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "online_cookbook"
app.config["MONGO_URI"] = "mongodb://turnpike:n0tt00late@ds253203.mlab.com:53203/online_cookbook"

mongo = PyMongo(app)



@app.route("/")
def index():
    return render_template("index.html", categories=mongo.db.categories.find())
    
@app.route("/add_recipe")
def add_recipe():
    return render_template("add_recipe.html", health_concerns=data_functions.health_concerns_list, recipe_type=data_functions.recipe_type_list, main_ing=data_functions.main_ing_list)
    
@app.route("/insert_recipe", methods=["POST"])
def insert_recipe():
    form = request.form.to_dict()
    data = data_functions.build_dict(form)
    recipes = mongo.db.recipes
    recipes.insert_one(data)
    return redirect(url_for('index'))
    
@app.route("/add_category")
def add_category():
    return render_template("add_category.html", categories=mongo.db.categories.find())
    
@app.route("/insert_category", methods=["POST"])
def insert_category():
    categories =  mongo.db.categories
    categories.insert_one(request.form.to_dict())
    return redirect(url_for('add_recipe'))

@app.route("/results")
def results():
    return render_template("results.html", recipes=mongo.db.recipes.find())
    
@app.route("/recipe/<recipe_id>")
def recipePage(recipe_id):
    current_recipe =  mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    rating = int(current_recipe["rating"])
    ingredients = data_functions.build_ings_to_display(current_recipe)
    method = data_functions.build_method_to_display(current_recipe)
    return render_template("recipe.html", recipe=current_recipe, rating=rating, ingredients=ingredients, method=method)
    

    
if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)