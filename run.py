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
    health_concerns_list = data_functions.build_list("health_concerns")
    recipe_type_list = data_functions.build_list("recipe_type")
    main_ing_list = data_functions.build_list("main_ing")
    return render_template("add_recipe.html", health_concerns=health_concerns_list, recipe_type=recipe_type_list, main_ing=main_ing_list)
    
@app.route("/insert_recipe", methods=["POST"])
def insert_recipe():
    data = data_functions.build_dict(request.form)
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
    serving = current_recipe["serves"]
    method = data_functions.build_method_to_display(current_recipe)
    return render_template("recipe.html", 
                            recipe=current_recipe, 
                            rating=rating, 
                            method=method,
                            serves=serving)
    
@app.route("/edit_recipe/<recipe_id>")
def edit_recipe(recipe_id):
    current_recipe =  mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    health_concerns_list = data_functions.build_list("health_concerns")
    recipe_type_list = data_functions.build_list("recipe_type")
    main_ing_list = data_functions.build_list("main_ing")
    method = data_functions.build_method_to_display(current_recipe)
    return render_template("edit_recipe.html", 
                            recipe=current_recipe, 
                            health_concerns=health_concerns_list, 
                            recipe_type=recipe_type_list, 
                            main_ing=main_ing_list, 
                            method=method)
    
@app.route("/update_recipe/<recipe_id>", methods=["POST"])
def update_recipe(recipe_id):
    recipes = mongo.db.recipes
    data = data_functions.build_dict(request.form)
    recipes.update( {'_id': ObjectId(recipe_id)}, data)
    return redirect(url_for('recipePage', recipe_id=recipe_id))
    
if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)