import os, pymongo

from flask import Flask, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "online_cookbook"
app.config["MONGO_URI"] = "mongodb://turnpike:n0tt00late@ds253203.mlab.com:53203/online_cookbook"

mongo = PyMongo(app)



@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/add_recipe")
def add_recipe():
    return render_template("add_recipe.html")

@app.route("/results")
def results():
    return render_template("results.html", recipes=mongo.db.recipes.find())
    
@app.route("/recipe/<recipe_id>")
def recipePage(recipe_id):
    current_recipe =  mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    rating = int(current_recipe["rating"])
    return render_template("recipe.html", recipe=current_recipe, rating=rating)
    

    
if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)