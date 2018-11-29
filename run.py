import os, pymongo, data_functions, json

from flask import Flask, render_template, url_for, request, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_uploads import UploadSet, configure_uploads, IMAGES #Required for image uploads

app = Flask(__name__)

#config for image uploads
images = UploadSet('images', IMAGES)
app.config["UPLOADED_IMAGES_DEST"] = "static/img/uploads"
configure_uploads(app, images)

#config for db access
app.config["MONGO_DBNAME"] = "online_cookbook"
app.config["MONGO_URI"] = "mongodb://turnpike:n0tt00late@ds253203.mlab.com:53203/online_cookbook"
mongo = PyMongo(app)


"""
Global Variables
"""
health_concerns_list = data_functions.build_list("health_concerns")
recipe_type_list = data_functions.build_list("recipe_type")
main_ing_list = data_functions.build_list("main_ing")


"""
Home page
"""

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
    #function to reset browse.html page to show all recipe
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
    #function to allow filtering on browse.html with 3 select elements
    form = request.form.to_dict()
    print(len(form))
    results = data_functions.build_query_for_filtering(form)
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
    #supplies the data for add_recipe.html
    health_concerns_list = data_functions.build_list("health_concerns")
    recipe_type_list = data_functions.build_list("recipe_type")
    main_ing_list = data_functions.build_list("main_ing")
    return render_template("add_recipe.html", health_concerns=health_concerns_list, recipe_type=recipe_type_list, main_ing=main_ing_list)
    
@app.route("/insert_recipe", methods=["POST"])
def insert_recipe():
    #inserts a new recipe into the database
    if 'image' in request.files:
        #uploads image to static/img/uploads and creates the filepath to store in the database
        filename = images.save(request.files['image'])
        filepath = "static/img/" + filename
    else:
        filepath = "https://media.istockphoto.com/photos/place-setting-picture-id513623454?s=2048x2048"
    data = data_functions.build_dict(request.form, filepath)
    mongo.db.recipes.insert_one(data)
    return redirect(url_for('index'))
    
@app.route("/add_category")
def add_category():
    #supplies the data for add_category.html
    return render_template("add_category.html", categories=mongo.db.categories.find())
    
@app.route("/insert_category", methods=["POST"])
def insert_category():
    #inserts a new category into the database
    categories =  mongo.db.categories
    data = {"cat_name" : request.form['cat_name'].lower(), "cat_type" : request.form['cat_type'].lower()}
    categories.insert_one(data)
    return redirect(url_for('add_recipe'))

    
@app.route("/search/<search_term>", methods=["GET", "POST"])
def search(search_term):
    #runs the search query based on user input and returns a list of results.
    mongo.db.recipes.create_index([('name', 'text')])
    query = ( { "$text": { "$search": search_term } } )
    results = mongo.db.recipes.find(query)
    return render_template("results.html",
                            recipes=results,
                            search_term=search_term)


    
@app.route("/recipe/<recipe_id>")
def recipePage(recipe_id):
    #supplies the data to display on recipe.html
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
    #supplies the data to display on edit_recipe.html
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
    #updates the edited recipe in the database
    if 'image' in request.files:
        #uploads image to static/img/uploads and creates the filepath to store in the database
        filename = images.save(request.files['image'])
        filepath = "static/img/" + filename
    else:
        filepath = "https://media.istockphoto.com/photos/place-setting-picture-id513623454?s=2048x2048"
    recipes = mongo.db.recipes
    data = data_functions.build_dict(request.form, filepath)
    recipes.update( {'_id': ObjectId(recipe_id)}, data)
    return redirect(url_for('recipePage', recipe_id=recipe_id))
    
if __name__ == '__main__':                  #prevents the app from running if imported by another file
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)