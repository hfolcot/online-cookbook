import os, pymongo

from flask import Flask, render_template, url_for, request, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

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

def sort_ingredients(form):
    #Build the list to push into the 'ingredients' heading of the recipe dict         
    ingredients = []  
    count = 1
    for item, value in form.items():
        for item, value in form.items(): #Running the for loop inside another for loop ensures that the loop begins again after each result is found.
            if item == "ing_name_{0}".format(count):
                ingredient = {item : value}
                for item, value in form.items(): #for loop is run again for every ing_name that is found to locate the matching ing_amount before the count is incremented.
                    if item == 'ing_amount_{0}'.format(count):
                        amount = {item : value}
                        ingredient.update(amount)
                count += 1
                ingredients.append(ingredient)
                break #return to the outer loop once a result is found
    return ingredients

def sort_method(form):
    #Build the list to push into the 'method' heading of the recipe dict   
    method = []
    count = 1
    for item, value in form.items():
        for item, value in form.items():
            if item == 'step_no_{0}'.format(count):
                step = {item: value}
                for item, value in form.items():
                    if item == "step_desc_{0}".format(count):
                        description = {item:value}
                        step.update(description)
                        break
                count += 1
                method.append(step)
                break
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


def build_dict(form):
    #Build a nested dictionary from the data in the add recipe form to send to db
    recipe = {"name" : form['name'], 
              "image" : form['image'],
              "ingredients" : [],
              "method" : [],
              "prep_time" : form['prep_time'],
              "cook_time" : form['cook_time'],
              "serves" : form['serves'],
              "author" : form['author'],
              "categories" : [],
              "rating" : form['rating']
              }
              
    recipe["ingredients"] = sort_ingredients(form)
    recipe["method"] = sort_method(form)
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
    count = 1
    displayed_method = {}
    for i in method:
        value = (str(i['step_no_{0}'.format(count)]) + ": " + i['step_desc_{0}'.format(count)].capitalize())
        displayed_method[count] = value
        count += 1
    return displayed_method
