import os, pymongo, data_functions, json

from flask import Flask, render_template, url_for, request, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
app = Flask(__name__)

app.config["MONGO_DBNAME"] = "online_cookbook"
app.config["MONGO_URI"] = "mongodb://turnpike:n0tt00late@ds253203.mlab.com:53203/online_cookbook"

mongo = PyMongo(app)


"""
Global Variables
"""
health_concerns_list = data_functions.build_list("health_concerns")
recipe_type_list = data_functions.build_list("recipe_type")
main_ing_list = data_functions.build_list("main_ing")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form['action'] == 'search':
            search_term = request.form['search']
            if search_term == "":
                error = "Please enter a value to search"
                return render_template('index.html', error=error)
            return redirect(url_for('search', search_term=search_term))
        elif request.form['action'] == 'browse':
           return redirect(url_for('get_all_recipes'))
    return render_template("index.html")

@app.route('/get_all_recipes')
def get_all_recipes():
    results = mongo.db.recipes.find()
    results_count = data_functions.count_results(results)
    return render_template("browse.html", 
                            recipes=results, 
                            health_concerns=health_concerns_list, 
                            main_ing=main_ing_list, 
                            recipe_type=recipe_type_list,
                            results_count = results_count)

@app.route("/filter_results", methods=["GET", "POST"])
def filter_results():
    form = request.form.to_dict()
    print(len(form))
    if len(form) == 0:
            return redirect(url_for('get_all_recipes'))
    elif len(form) == 1:
        for key, value in form.items():
            subcatname = key
            subcatvalue = value
        category = "categories." + subcatname
        results = mongo.db.recipes.find({category : { subcatvalue : "on" }})
    elif len(form) == 2:
        if "main_ing" in form:
            print("yes")
            cat1 = "categories.main_ing"
            value1 = str(form['main_ing'])
            if "recipe_type" in form:
                cat2 = "categories.recipe_type"
                value2 = str(form["recipe_type"])
            else:
                cat2 = "categories.health_concerns"
                value2 = str(form["health_concerns"])
        else:
            cat1 = "categories.health_concerns"
            value1 = str(form["health_concerns"])
            cat2 = "categories.recipe_type"
            value2 = str(form["recipe_type"])
        results = mongo.db.recipes.find({cat1 : { value1 : "on" }} and {cat2 : {value2: "on"}})
    elif len(form) == 3:
        cat1 = "categories.main_ing"
        value1 = str(form["main_ing"])
        cat2 = "categories.recipe_type"
        value2 = str(form['recipe_type'])
        cat3 = "categories.health_concerns"
        value3 = str(form['health_concerns'])
        results = mongo.db.recipes.find( { '$and': [ {cat1 : { value1 : "on" }}, {cat2 : {value2: "on"}}, {cat3 : {value3: "on"}} ] } )
    error = ''
    results_count = data_functions.count_results(results)
    if  results_count == 0:
        error = "No results found"
    return render_template("browse.html", 
                            recipes=results, 
                            health_concerns=health_concerns_list, 
                            main_ing=main_ing_list, 
                            recipe_type=recipe_type_list,
                            error=error,
                            results_count = results_count)

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
    data = {"cat_name" : request.form['cat_name'].lower(), "cat_type" : request.form['cat_type'].lower()}
    categories.insert_one(data)
    return redirect(url_for('add_recipe'))

    
@app.route("/search/<search_term>", methods=["GET", "POST"])
def search(search_term):
    mongo.db.recipes.create_index([('name', 'text')])
    query = ( { "$text": { "$search": search_term } } )
    results = mongo.db.recipes.find(query)
    return render_template("results.html",
                            recipes=results,
                            search_term=search_term)



@app.route("/browse/<browse>", methods=["GET", "POST"])
def browse(browse):
    browseTerm = str(browse) #changing variable from unicode to string
    print(browseTerm)
    health_concerns_list = data_functions.build_list("health_concerns")
    recipe_type_list = data_functions.build_list("recipe_type")
    main_ing_list = data_functions.build_list("main_ing")
    print("I am here!")
    if browseTerm in health_concerns_list:
        print("it's a health concern")
        query =  {"categories": [{ "health_concerns" : { browseTerm.lower(): "on" }}]} 
    elif browseTerm in recipe_type_list:
        print("it's a recipe type")
        query =  {"categories": [{ "recipe_type" : { browseTerm.lower(): "on" }}]}
    elif browseTerm in main_ing_list:
        print("it's a main ingredient")
        query =  {"categories": [{ "main_ing" : { browseTerm.lower(): "on" }}]}
    print(query)
    results = mongo.db.recipes.find(query)
    print(results)
    for result in results:
        print("found one!")
        if not result:
            print("No results")
    return render_template("results.html", recipes=results)
    
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