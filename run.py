import os, pymongo

from flask import Flask, render_template, url_for
from flask_pymongo import PyMongo

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
    
@app.route("/recipe")
def recipePage():
    return render_template("recipe.html")
    

    
if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)