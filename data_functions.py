import os, pymongo, json

from flask import Flask
from flask_pymongo import PyMongo


app = Flask(__name__)

app.config["MONGO_DBNAME"] = "online_cookbook"
app.config["MONGO_URI"] = "mongodb://turnpike:n0tt00late@ds253203.mlab.com:53203/online_cookbook"

mongo = PyMongo(app)

"""
Categories:
The categories are the most heavily nested section of each recipe document.
"""


def build_list(cat_type):
    """
    Build a list of categories for each of the three types of category.
    Called by run.py on startup and used by multiple functions.
    """
    categories = mongo.db.categories.find()
    cats = []
    for i in categories:
        cats.append(i)
    output = []
    for i in cats:
        if i["cat_type"] == cat_type:
            new_item = (i["cat_name"])
            output.append(new_item)
    return output



"""
Packing up the data to send to the database:
Because of the nested nature of the database documents, it is necessary to build this 
structure from user input before uploading to the database.
"""

def sort_method(form):
    """
    Build the list to push into the 'method' key of the recipe dict. Items are
    numbered automatically using the form and stored in the db as a key:value of 
    step number : method details
    """
    method = {}
    count = 1
    for item in form:
        for item, value in form.items():
            if item.isdigit():
                if int(item) == count:
                    step = {item : value}
                    method.update(step)
                    count += 1
    return method
    
def sort_categories(form):
    """
    Build a nested list of categories based on their type and then return to the 
    main build_dict function 
    """
    categories = {'health_concerns': {}, 
                  'main_ing'  : {}, 
                  'recipe_type' : {}}
    if 'recipe_type' in form:
        categories['recipe_type'] = form['recipe_type']
    if 'main_ing' in form:
        categories['main_ing'] = form['main_ing']
    if 'health_concerns' in form:
        categories['health_concerns'] = form['health_concerns']
    return categories

    
    
def build_dict(form, filepath):
    """
    Build a full dict ready to send to the db in the correct nested format.
    """
    flatFalseForm = form.to_dict(flat=False) #Allows access to the list of ingredients in the form - without this it will only return the first item
    recipe = {"name" : form['name'].lower(), 
              "ingredients" : flatFalseForm['ingredients'],
              "image" : filepath,
              "method" : [],
              "prep_time" : form['prep_time'],
              "cook_time" : form['cook_time'],
              "serves" : form['serves'],
              "author" : form['author'],
              "categories" : {},
              "ratings" : {"number_times_rated" : 0, "score" : 0, "rating" : 0}
              }
    recipe['method'] = sort_method(form)
    recipe['categories'] = sort_categories(form)
    return recipe
    
    
"""
Unpacking the data when retrieving from the database.
"""

def build_method_to_display(recipe):
    """
    Build a list to diplay on the recipe page in the correct order of steps.
    """
    method = recipe['method']
    returned_method = []
    count = 1
    for item in method:
        for k,v in method.items():
            if int(k) == count:
                step = str(k) + ": " + v
                returned_method.append(step)
                break
        count += 1    
    return sorted(returned_method)

"""
Result filtering
"""

def count_results(results):
    """
    Count the number of results returned
    """
    number_of_recipes = 0
    for result in results:
        number_of_recipes += 1
    results.rewind()
    return number_of_recipes
    
def build_query_for_filtering(form):
    """
    Build the correct query to filter recipes by category, based on user selection
    """
    if len(form) == 1:
        for key, value in form.items():
            cat1 = 'categories.' + key
            value1 = value
            query = {cat1 : value1}
    elif len(form) == 2:
        if "main_ing" in form:
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
        query = ( {'$and' : [{ cat1: value1 }, { cat2 : value2}]} )
    elif len(form) == 3:
        cat1 = "categories.main_ing"
        value1 = str(form["main_ing"])
        cat2 = "categories.recipe_type"
        value2 = str(form['recipe_type'])
        cat3 = "categories.health_concerns"
        value3 = str(form['health_concerns'])
        query = { '$and': [ {cat1 : value1}, {cat2 : value2}, {cat3 : value3} ] }
    return query
