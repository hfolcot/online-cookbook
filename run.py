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
                return redirect(url_for('index', error=error, user=g.user))
            return redirect(url_for('search', 
                                     search_term=search_term,
                                     page_no=1))
    return render_template("index.html", user=g.user)
    
"""
Login/User sessions
"""

@app.route('/login', methods=['GET'])
#Check that the username is found in the database and the password is valid
#Called by script.js on click of login button in login modal
def check_password():
    u = request.args.get('u')
    p = request.args.get('p')
    print(u)
    print(p)
    user = mongo.db.users.find({"username" : u})
    count = 0
    for item in user:
        print("hi " + u)
        count += 1
        if count == 1:
            print("User found")
            if p == item['password']:
                print("password correct")
                session['user'] = u
                message = "You were successfully logged in"
                return message
            else:
                print("incorrect password")
                message = "Incorrect password"
                return message
    if count == 0:
        print("user not found")
        message="User not found"
        return message    


@app.route('/logout')
def end_session():
    session.pop('user', None)
    return redirect(url_for('index'))
    
@app.route('/create_user', methods=['GET'])
def create_user():
    #Creates a new user in the database if that user does not already exist
    #Called by script.js on click of create account button in create user modal
    u = request.args.get('u')
    p = request.args.get('p')
    session.pop('user', None) #ensures there is not currently an active session
    #Check that the username is not already taken
    user = mongo.db.users.find({"username" : u})
    count = 0
    for item in user:
        count += 1
        if count > 0:
            message = "That username has already been taken"
            return message
    if count == 0:
        mongo.db.users.insert_one({"username" : u, "password" : p})
        session['user'] = u
        message = "User created, you will now be logged in"
        return message
    
    
@app.before_request
def before_request():
#checks to see if the user is logged in before each request
    g.user = None
    if 'user' in session:
        print("user is in session")
        g.user = session['user']
    else:
        print("user not in session")
    
"""
Recipe Methods
"""


@app.route('/get_recipes/<page_no>', methods=['GET', 'POST'])
def get_recipes(page_no):
    #function to reset browse.html page to show all recipes in paginated list
    skip_count = (int(page_no) - 1) * 8 #this is the number of results to skip when searching in mongodb to find the next page's worth of results
    if request.method == 'POST':
        form = request.form.to_dict()
        print("Form: ")
        print(form)
        query = data_functions.build_query_for_filtering(form)
        non_paginated_results = mongo.db.recipes.find(query).sort([("rating", pymongo.DESCENDING), ("_id", pymongo.ASCENDING)]) #To count the total number of results
        results_count = data_functions.count_results(non_paginated_results) #To count the total number of results
        paginated_results = mongo.db.recipes.find(query).sort([("rating", pymongo.DESCENDING), ("_id", pymongo.ASCENDING)]).skip(skip_count).limit(8)
    else:
        results = mongo.db.recipes.find()
        results_count = data_functions.count_results(results)
        paginated_results = mongo.db.recipes.find().sort([("rating", pymongo.DESCENDING), ("_id", pymongo.ASCENDING)]).skip(skip_count).limit(8)
    total_page_no=int(math.ceil(results_count/8.0))
    return render_template("browse.html", 
                            recipes=paginated_results, 
                            health_concerns=health_concerns_list, 
                            main_ing=main_ing_list, 
                            recipe_type=recipe_type_list,
                            results_count = results_count,
                            user=g.user,
                            page_no=page_no,
                            total_page_no=total_page_no
                            )


    
@app.route("/search/<search_term>/<page_no>", methods=["GET", "POST"])
def search(search_term, page_no):
    #runs the search query based on user input and returns a list of paginated results.
    mongo.db.recipes.create_index([('name', 'text')])
    query = ( { "$text": { "$search": search_term } } )
    results = mongo.db.recipes.find(query)
    results_count = data_functions.count_results(results)
    skip_count = (int(page_no) - 1) * 8 #this is the number of results to skip when searching in mongodb to find the next page's worth of results
    paginated_results = mongo.db.recipes.find(query).sort([("rating", pymongo.DESCENDING), ("_id", pymongo.ASCENDING)]).skip(skip_count).limit(8)
    total_page_no=int(math.ceil(results_count/8.0))
    return render_template("results.html", 
                            recipes=paginated_results, 
                            health_concerns=health_concerns_list, 
                            main_ing=main_ing_list, 
                            recipe_type=recipe_type_list,
                            results_count = results_count,
                            user=g.user,
                            page_no=page_no,
                            total_page_no=total_page_no
                            )

@app.route("/add_recipe")
def add_recipe():
    #supplies the data for add_recipe.html
    if g.user:
        health_concerns_list = data_functions.build_list("health_concerns")
        recipe_type_list = data_functions.build_list("recipe_type")
        main_ing_list = data_functions.build_list("main_ing")
        return render_template("add_recipe.html", health_concerns=health_concerns_list, recipe_type=recipe_type_list, main_ing=main_ing_list, user=g.user)
    else:
        return redirect(url_for('index'))
    
@app.route("/insert_recipe", methods=["POST"])
def insert_recipe():
    #inserts a new recipe into the database
    if 'image' in request.files:
        #uploads image to static/img/uploads and creates the filepath to store in the database
        filename = images.save(request.files['image'])
        filepath = "../static/img/uploads/" + filename
    else:
        filepath = "https://media.istockphoto.com/photos/place-setting-picture-id513623454?s=2048x2048"
    data = data_functions.build_dict(request.form, filepath)
    newid = mongo.db.recipes.insert_one(data)
    return redirect(url_for('recipePage', recipe_id = newid.inserted_id))
    
@app.route("/add_category")
def add_category():
    #supplies the data for add_category.html
    return render_template("add_category.html", categories=mongo.db.categories.find(), user=g.user)
    
@app.route("/insert_category", methods=["POST"])
def insert_category():
    #inserts a new category into the database
    categories =  mongo.db.categories
    data = {"cat_name" : request.form['cat_name'].lower(), "cat_type" : request.form['cat_type'].lower()}
    categories.insert_one(data)
    return redirect(url_for('add_recipe'))



    
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
                            serves=serving,
                            user=g.user)
    
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
                            method=method,
                            user=g.user)
    
@app.route("/update_recipe/<recipe_id>", methods=["POST"])
def update_recipe(recipe_id):
    #updates the edited recipe in the database
    print(request.files)
    if 'image' in request.files:
        #uploads image to static/img/uploads and creates the filepath to store in the database
        filename = images.save(request.files['image'])
        filepath = "../static/img/uploads" + filename
    else:
        print("image not found")
        filepath = "https://media.istockphoto.com/photos/place-setting-picture-id513623454?s=2048x2048"
    recipes = mongo.db.recipes
    data = data_functions.build_dict(request.form, filepath)
    recipes.update( {'_id': ObjectId(recipe_id)}, data)
    return redirect(url_for('recipePage', recipe_id=recipe_id))
    
@app.route('/delete_recipe', methods=['GET'])
def delete_recipe():
    
    print("get request received")
    user = request.args.get('user')
    print(user)
    password = request.args.get('password')
    recipe_id = request.args.get('recipe_id')
    print(recipe_id)
    recipes = mongo.db.recipes
    deleted_recipes = mongo.db.deleted
    finduser = mongo.db.users.find({"username" : user})
    count = 0
    for item in finduser:
        print("hi " + item['username'])
        count += 1
        if count == 1:
            print("User found")
            if password == item['password']:
                print("password correct")
                for doc in recipes.find({'_id' : ObjectId(recipe_id)}):
                    document = doc #There should only be one document returned in the cursor as search is by id.
                deleted_recipes.insert_one(document) #Copies the recipe to the deleted collection
                deleted_recipes.update({'_id': ObjectId(recipe_id)}, {"$set" :{"deleted" : "on", "deleted_by" : user}}) #adds details of who has deleted the recipe
                recipes.remove({'_id': ObjectId(recipe_id)}) #removes the recipe from the active recipes collection
                message = "Recipe Deleted"
                return message
            else:
                print("incorrect password")
                message = "Incorrect password"
                return message
    if count == 0:
        print("user not found")
        message="User not found"
        return message
    
    
if __name__ == '__main__':                  #prevents the app from running if imported by another file
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)