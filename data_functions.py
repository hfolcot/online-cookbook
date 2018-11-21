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

def sort_method(form):
    #Build the list to push into the 'method' heading of the recipe dict   
    method = {}
    count = 1
    for item in form:
        for item, value in form.items():
            if item == str(count):
                print(item)
                step = {item : value}
                print(step)
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


def build_dict(form):
    #Build a nested dictionary from the data in the add recipe form to send to db
    flatFalseForm = form.to_dict(flat=False) #Allows access to the list of ingredients in the form - without this it will only return the first item
    recipe = {"name" : form['name'], 
              "image" : form['image'],
              "ingredients" : flatFalseForm['ingredients'],
              "method" : [],
              "prep_time" : form['prep_time'],
              "cook_time" : form['cook_time'],
              "serves" : form['serves'],
              "author" : form['author'],
              "categories" : [],
              "rating" : form['rating']
              }
    if form['image'] == "": 
        recipe['image'] = "https://media.istockphoto.com/photos/place-setting-picture-id513623454?s=2048x2048"
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
            if k == str(count):
                step = k + ": " + v.capitalize()
                print(step)
                returned_method.append(step)
                break
        count += 1    
    return sorted(returned_method)
