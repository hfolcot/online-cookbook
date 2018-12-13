import os, pymongo, data_functions, json, math

from flask import Flask, render_template, url_for, request, redirect, session, g, flash
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from flask_uploads import UploadSet, configure_uploads, IMAGES #Required for image uploads

app = Flask(__name__)
app.secret_key = os.urandom(24) #Creates a random string to use as session key

#config for image uploads
images = UploadSet('images', IMAGES)
app.config["UPLOADED_IMAGES_DEST"] = "static/img/uploads"
configure_uploads(app, images)

#config for db access
app.config["MONGO_DBNAME"] = "online_cookbook"
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)


"""
Global Variables
"""

#Build a list of the three main category headings, needed for multiple functions
health_concerns_list = data_functions.build_list("health_concerns")
recipe_type_list = data_functions.build_list("recipe_type")
main_ing_list = data_functions.build_list("main_ing")

"""
Home page
"""

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main welcome page with option to search, add or browse recipes.
    """
    if request.method == "POST":
        if request.form['action'] == 'search':
            search_term = request.form['search']
            if search_term == "":
                flash("Please enter a value to search")
                return redirect(url_for('index', user=g.user))
            for i in search_term:
                if not i.isalnum():
                    search_term= search_term.replace(i, "-")
            return redirect(url_for('search', 
                                     search_term=search_term,
                                     page_no=1))
    return render_template("index.html", user=g.user)
    
"""
Login/User sessions
"""

@app.route('/login', methods=['GET'])
def check_password():
    """
    Check that the username is found in the database and the password is valid
    Called by script.js on click of login button in login modal
    """
    u = request.args.get('u').lower()
    p = request.args.get('p')
    user = mongo.db.users.find_one({"username" : u})
    if not user:
        message="User not found"
        return message  
    if p == user['password']:
        session['user'] = u
        message = "You were successfully logged in"
        return message
    else:
        message = "Incorrect password"
        return message
  


@app.route('/logout')
def end_session():
    """
    Log the user out of the session and return them to the home page
    """
    session.pop('user', None)
    flash("You were successfully logged out")
    return redirect(url_for('index'))
    
@app.route('/create_user', methods=['GET'])
def create_user():
    """
    Creates a new user in the database if that user does not already exist
    Called by script.js on click of create account button in create user modal
    """
    u = request.args.get('u').lower()
    p = request.args.get('p')
    session.pop('user', None) #ensures there is not currently an active session
    #Check that the username is not already taken
    for letter in u:
        if not letter.isalnum():
            message = "Invalid characters in username. Please use alphanumeric only."
            return message
    for letter in p:
        if not letter.isalnum():
            message = "Invalid characters in password. Please use alphanumeric only."
            return message
    user = mongo.db.users.find_one({"username" : u})
    if user:
        message = "That username has already been taken"
        return message
    else:
        mongo.db.users.insert_one({"username" : u,
                                   "password" : p, 
                                   "rated_recipes" : []})
        session['user'] = u
        message = "User created, you will now be logged in"
        return message
    
    
@app.before_request
def before_request():
    """
    Check to see if the user is logged in before each request
    """
    g.user = None
    if 'user' in session:
        g.user = session['user']
    
"""
Recipe Read Methods
"""

@app.route('/get_recipes/<page_no>', methods=['GET', 'POST'])
def get_recipes(page_no):
    """
    Reset browse.html page to show all recipes in paginated list
    """
    selected_recipe_type = None
    selected_main_ing = None
    selected_health_concerns = None
    #this is the number of results to skip when searching in mongodb to find 
    #the next page's worth of results:
    skip_count = (int(page_no) - 1) * 8 
    if request.method == 'POST':
        #User has selected to filter by category
        form = request.form.to_dict()
        if 'recipe_type'in form:
            selected_recipe_type = form['recipe_type']
        if 'main_ing' in form:
            selected_main_ing = form['main_ing']
        if 'health_concerns' in form:
            selected_health_concerns = form['health_concerns']
        if len(form) == 0:
            #catch for if user clicks update button without selecting a filtering option
            flash("Please choose a category to filter")
            return redirect(url_for('get_recipes', page_no=1))
        query = data_functions.build_query_for_filtering(form)
        #To give to the count_results function to count the total number of results:
        non_paginated_results = mongo.db.recipes.find(query).sort([("rating", pymongo.DESCENDING), 
                                                                 ("_id", pymongo.ASCENDING)]) 
        #Count the total number of results:
        results_count = data_functions.count_results(non_paginated_results)
        #To return only 8 results to display on the given page number:
        paginated_results = mongo.db.recipes.find(query).sort([("rating", pymongo.DESCENDING), 
                                                               ("_id", pymongo.ASCENDING)]).skip(skip_count).limit(8) 
    else:
        #Show all results (paginated)
        results = mongo.db.recipes.find()
        results_count = data_functions.count_results(results)
        paginated_results = mongo.db.recipes.find().sort([("ratings.rating", pymongo.DESCENDING), 
                                                        ("_id", pymongo.ASCENDING)]).skip(skip_count).limit(8)
    #calculate how many pages of results will be required:
    total_page_no=int(math.ceil(results_count/8.0))
    #For the html page to show 0 of 0 pages if no results:
    if results_count == 0:
        page_no = 0
    return render_template("browse.html", 
                            recipes=paginated_results, 
                            health_concerns=health_concerns_list, 
                            main_ing=main_ing_list, 
                            recipe_type=recipe_type_list,
                            results_count = results_count,
                            user=g.user,
                            page_no=page_no,
                            total_page_no=total_page_no,
                            selected_recipe_type = selected_recipe_type,
                            selected_main_ing = selected_main_ing,
                            selected_health_concerns = selected_health_concerns
                            )


    
@app.route("/search/<search_term>/<page_no>", methods=["GET", "POST"])
def search(search_term, page_no):
    """
    Runs the search query based on user input and returns a list of paginated 
    results.
    """
    mongo.db.recipes.create_index([('name', 'text')])
    query = ( { "$text": { "$search": search_term } } )
    #return all results and then count how many there are
    results = mongo.db.recipes.find(query)
    results_count = data_functions.count_results(results)
    #Split the results into blocks of 8 depending on which page number has been 
    #requested.
    #Skip_count is the number of results to skip when searching in mongodb to 
    #find the next page's worth of results
    skip_count = (int(page_no) - 1) * 8
    paginated_results = mongo.db.recipes.find(query).sort([("ratings.rating", pymongo.DESCENDING), 
                                                           ("_id", pymongo.ASCENDING)]).skip(skip_count).limit(8)
    total_page_no=int(math.ceil(results_count/8.0))
    if results_count == 0:
        page_no = 0
    return render_template("results.html",
                            search_term=search_term,
                            recipes=paginated_results, 
                            health_concerns=health_concerns_list, 
                            main_ing=main_ing_list, 
                            recipe_type=recipe_type_list,
                            results_count = results_count,
                            user=g.user,
                            page_no=page_no,
                            total_page_no=total_page_no
                            )
                            
    
@app.route("/recipe/<recipe_id>")
def recipePage(recipe_id):
    """
    Supplies the data to display on recipe.html
    """
    current_recipe =  mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    rating = int(current_recipe['ratings']['rating'])
    serving = current_recipe["serves"]
    method = data_functions.build_method_to_display(current_recipe)
    user = mongo.db.users.find({'username' : g.user})
    user_recipes_rated = []
    for u in user:
        user_recipes_rated = u['rated_recipes']
    return render_template("recipe.html", 
                            recipe=current_recipe, 
                            rating=rating, 
                            method=method,
                            serves=serving,
                            user=g.user,
                            user_rated=user_recipes_rated,
                            recipe_id=recipe_id)

"""
Recipe Create/Update/Delete Methods
"""

@app.route("/add_recipe")
def add_recipe():
    """
    Supplies the data for add_recipe.html, will only return data if user is 
    logged in
    """
    if g.user: 
        health_concerns_list = data_functions.build_list("health_concerns")
        recipe_type_list = data_functions.build_list("recipe_type")
        main_ing_list = data_functions.build_list("main_ing")
        return render_template("add_recipe.html", 
                                health_concerns=health_concerns_list, 
                                recipe_type=recipe_type_list,
                                main_ing=main_ing_list, 
                                user=g.user)
    else:
        flash("You must be logged in to add a recipe")
        return redirect(url_for('index'))
    
@app.route("/insert_recipe", methods=["POST"])
def insert_recipe():
    """
    Insert a new recipe into the database
    """
    if 'image' in request.files:
        #uploads image to static/img/uploads and creates the filepath to store 
        #in the database
        filename = images.save(request.files['image'])
        filepath = "../static/img/uploads/" + filename
    else:
        filepath = "../static/img/not-found.jpg"
    data = data_functions.build_dict(request.form, filepath)
    newid = mongo.db.recipes.insert_one(data)
    return redirect(url_for('recipePage', recipe_id = newid.inserted_id))


@app.route('/rate/<recipe_id>', methods=["POST"])
def rate_recipe(recipe_id):
    """
    Calculates the new rating based on user input.
    Function not accessible to users unless logged in.
    """
    mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, 
                                { '$inc': 
                                    {'ratings.score': int(request.form['rating']), 
                                    'ratings.number_times_rated': 1 } })
    mongo.db.users.update_one({"username": g.user}, 
                                    {'$addToSet' : 
                                        {"rated_recipes" : recipe_id}})
    current_recipe =  mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    rating = int(current_recipe["ratings"]['score']) / int(current_recipe["ratings"]['number_times_rated'])
    mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, 
                                { '$set': {'ratings.rating': rating}})
    return redirect(url_for('recipePage', recipe_id = recipe_id))

    
@app.route("/edit_recipe/<recipe_id>")
def edit_recipe(recipe_id):
    """
    Supplies the data to display on edit_recipe.html
    Function not accessible to users unless logged in.
    """
    if g.user:
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
                                method=method,
                                user=g.user)
    else:
        flash("You must be logged in to edit recipes")
        return redirect(url_for('index'))
    
@app.route("/update_recipe/<recipe_id>", methods=["POST"])
def update_recipe(recipe_id):
    """
    Updates the edited recipe in the database
    """
    if 'image' in request.files:
        #uploads image to static/img/uploads and creates the filepath to store 
        #in the database
        filename = images.save(request.files['image'])
        filepath = "../static/img/uploads/" + filename
    elif 'filepath' in request.form:
        filepath = request.form['filepath']
    else:
        filepath = "../static/img/not-found.jpg"
    recipes = mongo.db.recipes
    data = data_functions.build_dict(request.form, filepath)
    recipes.update( {'_id': ObjectId(recipe_id)}, data)
    return redirect(url_for('recipePage', recipe_id=recipe_id))
    
@app.route('/delete_recipe', methods=['GET'])
def delete_recipe():
    """
    Called by the #delete-recipe button on recipe.html(#delete-recipe-modal), 
    which runs a get request through script.js.
    The user can only do this if they are logged in and they must confirm their 
    credentials.
    Once a password has been entered and validated, the recipe document in the 
    db will be updated with a 'deleted : on' and the name of the user who has 
    authorised the delete.
    """
    user = request.args.get('user')
    password = request.args.get('password')
    recipe_id = request.args.get('recipe_id')
    recipes = mongo.db.recipes
    deleted_recipes = mongo.db.deleted
    username = mongo.db.users.find_one({"username" : user})
    #check user exists
    if not username:
        message="User not found"
        return message
    #check password and delete recipe if correct
    if password == username['password']:
        document =  recipes.find_one({'_id' : ObjectId(recipe_id)})
        #Copy the recipe to the deleted collection:
        deleted_recipes.insert_one(document)
        #add details of who has deleted the recipe:
        deleted_recipes.update({'_id': ObjectId(recipe_id)}, 
                                                {"$set" :
                                                    {"deleted" : "on", 
                                                    "deleted_by" : user}})
        #remove the recipe from the active recipes collection:    
        recipes.remove({'_id': ObjectId(recipe_id)})
        message = "Recipe Deleted"
        return message
    else:
        message = "Incorrect password"
        return message


"""
Category adding
"""
    
@app.route("/add_category")
def add_category():
    """
    Supplies the data for add_category.html
    """
    if g.user:
        return render_template("add_category.html",
                            health_concerns=health_concerns_list, 
                            recipe_type=recipe_type_list, 
                            main_ing=main_ing_list,  
                            user=g.user)
    else:
        flash("You must be logged in to manage categories")
        return redirect(url_for('index'))
    
@app.route("/insert_category", methods=["POST"])
def insert_category():
    """
    Inserts a new category into the database
    """
    if request.form['cat_type'] == '':
        flash("Please select a category type")
        return redirect(url_for('add_category'))
    else:
        data = {"cat_name" : request.form['cat_name'].lower(), "cat_type" : request.form['cat_type'].lower()}
        mongo.db.categories.insert_one(data)
        flash("Category Added")
        return redirect(url_for('index'))
    
@app.route("/delete_category", methods=["POST"])
def delete_category():
    """
    Removes a category from the database
    """
    if len(request.form) == 0:
        flash("Please select a category")
        return redirect(url_for('add_category'))
    else:
        for k, v in request.form.items():
            mongo.db.categories.delete_one({"cat_name" : v})
        flash("Category deleted")
        return redirect(url_for('index'))
    
    
"""
Error handling
"""

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def something_wrong(error):
    return render_template('500.html'), 500

"""
Run the app
"""
if __name__ == '__main__':   
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=False)