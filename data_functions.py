import os, pymongo, json

from flask import Flask, url_for, redirect, flash
from flask_pymongo import PyMongo


app = Flask(__name__)

app.config["MONGO_DBNAME"] = "online_cookbook"
app.config["MONGO_URI"] = "mongodb://turnpike:n0tt00late@ds253203.mlab.com:53203/online_cookbook"

mongo = PyMongo(app)

categories = mongo.db.categories.find() #Creates the cursor for the collection 'Categories' in the database

#Create a local variable to prevent repeated calls to the database
cats = []
for i in categories:
    cats.append(i)


def build_list(cat_type):
    #Build a list of categories for each category type
    output = []
    for i in cats:
        if i["cat_type"] == cat_type:
            new_item = (i["cat_name"])
            output.append(new_item)
    return output



"""
Packing up the data to send to the database
"""

def sort_method(form):
    #Build the list to push into the 'method' heading of the recipe dict   
    method = {}
    print(form)
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
    #Organise the categories to push into the recipe dict
    categories = {'health_concerns': {}, 
                  'main_ing'  : {}, 
                  'recipe_type' : {}}
    health_concerns_list = build_list("health_concerns")
    main_ing_list = build_list("main_ing")
    recipe_type_list = build_list("recipe_type")
    for item, value in form.items():
        if item in health_concerns_list:
            category = {item : value}
            categories['health_concerns'].update(category)
        elif item in main_ing_list:
            category = {item : value}
            categories['main_ing'].update(category)
        elif item in recipe_type_list:
            category = {item : value}
            categories['recipe_type'].update(category)
    return categories

    
    
def build_dict(form, filepath):
    #Build a nested dictionary from the data in the add recipe form to send to db
    flatFalseForm = form.to_dict(flat=False) #Allows access to the list of ingredients in the form - without this it will only return the first item
    recipe = {"name" : form['name'].lower(), 
              "ingredients" : flatFalseForm['ingredients'],
              "image" : filepath,
              "method" : [],
              "prep_time" : form['prep_time'],
              "cook_time" : form['cook_time'],
              "serves" : form['serves'],
              "author" : form['author'],
              "categories" : [],
              "ratings" : {"number_times_rated" : 0, "score" : 0, "rating" : 0}
              }
    recipe['method'] = sort_method(form)
    recipe['categories'] = [sort_categories(form)]
    return recipe
    
    
"""
Unpacking the data when retrieving from the database
"""

def build_ings_to_display(recipe):
    #Pair up the ingredients and amounts and return a single value for each
    ingredients = recipe['ingredients']
    count = 1
    displayed_ingredients = {}
    for i in ingredients:
        value = (i['ing_amount_{0}'.format(count)] + " " + i['ing_name_{0}'.format(count)])
        displayed_ingredients[count] = value
        count += 1
    return displayed_ingredients

def build_method_to_display(recipe):
    #Pair up the step numbers with the associated step and return a single value for each
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
    #Count the number of results returned, minus the number marked as deleted
    number_of_recipes = 0
    for result in results:
        number_of_recipes += 1
    results.rewind()
    return number_of_recipes
    
def build_query_for_filtering(form):
    #determines which query should be used when filtering recipes list
    if len(form) == 1:
        for key, value in form.items():
            subcatname = key
            subcatvalue = value
            category = "categories." + subcatname
            query = {category : { subcatvalue : "on" }}
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
            query = {cat1 : { value1 : "on" }} and {cat2 : {value2: "on"}}
    elif len(form) == 3:
        cat1 = "categories.main_ing"
        value1 = str(form["main_ing"])
        cat2 = "categories.recipe_type"
        value2 = str(form['recipe_type'])
        cat3 = "categories.health_concerns"
        value3 = str(form['health_concerns'])
        query = { '$and': [ {cat1 : { value1 : "on" }}, {cat2 : {value2: "on"}}, {cat3 : {value3: "on"}} ] }
    return query
