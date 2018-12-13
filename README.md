# Online Cookbook by Heather Olcot

See the project live at https://online-cookbook-hev.herokuapp.com/

This is the online cookbook, where users can look up a list of recipes in a 
database and add their own. Recipes can be added, rated, edited and deleted by 
logged in users.

# UX

Documentation for the planning process can be found in the 'planning' folder 
[here](https://github.com/hfolcot/online-cookbook/tree/master/planning).

The final project has a few differences in layout from the designs done in the planning.
It was noted during development that these changes were necessary to provide a 
better user experience.

#### User stories:
1. As a vegan, I would like to be able to search through a list of recipes based 
on their type, in  order to avoid going through all ingredient lists.
2. As a cook, I would like to be able to store any recipes I create, in order to 
access and share with others.

# Features

## Existing Features
The application can be used with or without a user login, however some features 
are only available to logged in users.

Any user of the website is able to search for specific keywords in a recipe name
and view a list of results. The search function ONLY returns results with the search 
term in the recipe name, no categories or ingredients are searched. 

They can also browse all recipes and filter the list based on the attributes of 
that recipe. From the results they can then view a specific recipe's page. Results 
are always returned in order of rating; the highest rated recipe will be listed first.

Users can create an account, this is very basic in that usernames and passwords 
are stored in the database in a collection 'Users' in plain text (users are clearly 
warned of this insecure nature of the site when signing up and urged to use unique 
passwords, please see the Features Left to Implement section for further details).

Once an account has been created and users are logged in, they will have the option 
to add their own recipes and manage the recipe categories (adding and deleting).

Adding a recipe will create a new document in the database's 'Recipes' collection.
That recipe will then be available to search and view along with the rest.

From an existing recipe, a user will be able to edit or delete. If they choose to 
delete a recipe, the document in the database for that recipe will be moved to the 
database's 'Deleted' document collection and a field is added to show the username
of the user who has deleted the document.

Recipes can be rated by logged in users. Users can choose from between 1 and 5 and 
the recipe's ID will be added to an array in that user's database record to prevent 
them from rating multiple times.

The rating uses the following fields in the database record:
`    "ratings": {
        "number_times_rated": 0,
        "score": 0,
        "rating": 0
    }`
    
When a user clicks Rate, the `number_times_rated` field is incremented by 1 and the
amount they chose is added to the `score` field. The rating is then calculated by dividing 
the score by the number of times rated. This is then entered into the `rating` field.

The site also features custom 404 and 500 error pages.


## Features Left to Implement
#### Filtering
The original design of the recipes allowed for multiple categories to be selected 
when creating - however, this caused problems with the ability to filter accurately 
and it was decided that a simpler option would be to be able to select one category
per category heading (out of 'Main ingredient', 'Recipe Type' and 'Health'). At a 
later time I would like to go back to using multiple categories on recipes and filter
by selecting checkboxes and having a javascript ajax query get the data. Early attempts
at this method can be seen in the script.js commit dated 29th November 2018.

#### Editing
It may be worth keeping track of which users have edited a recipe by adding an array
to the document showing each individual edit such as:
```"edits" : [{"date" : 00/00/0000, "username" : "person", "fields_edited" : ['name', 'ingredients', 'image']```

#### Add recipe form
The form to add/edit a recipe is currently quite long, it could make for a better user 
experience to split this into two or three stages. 

#### User accounts
User accounts are not currently secure - some browsers will show a warning in the 
console when a user is prompted to enter a password because there is no SSL certificate.
The passwords are also stored in plain text which the user is made aware of.
It is an important requirement to make sure that user logins are made more secure.

#### User profiles
If a user has an account on a site such as this, they would expect to be able to go 
to a profile page where they can see their own recipes and edit from there. This is 
something that should be implemented in a future version.

#### Undo Delete
The recipes are currently moved to a different collection in the database rather 
than being completely deleted, which allows for an 'undo delete' feature to be added 
if necessary.

# Technologies Used
The main logic of this application is written in [Python](https://www.python.org) 
using the [Flask](http://flask.pocoo.org/) framework to handle the routes and 
page rendering, and [PyMongo](https://api.mongodb.com/python/current/) for CRUD operations.

Pages are written in [HTML](https://www.w3.org/html/) using 
[CSS3](https://www.w3.org/Style/CSS/Overview.en.html) for styling and 
[JavaScript](https://www.javascript.com/) for enhanced effects and some of the 
button functions, specifically with [JQuery](https://jquery.com/)to minimalise 
the amount of code required.

The main page layout and styles are from [materializecss](https://materializecss.com/).

The app uses two Python files, run.py for the main Flask app routing and the CRUD 
functions, and data_functions.py for all other functions such as sorting the data 
to insert into the database.

### Database
The site uses [MongoDB](https://www.mongodb.com/) for data storage and is hosted
at [MLab](https://mlab.com).

There are four collections in the database. A sample document from each collection 
can be found in the [database_schema](https://github.com/hfolcot/online-cookbook/tree/master/database_schema) 
folder.

Users: This is where user data is stored, including username, password and a list 
of recipes that have been rated by that user.

Categories: holds one document for each category, giving the name and type of 
category.

Recipes: The collection of all active recipes. Any deleted recipes are marked with 
the username of the user that deleted it and moved to the Deleted Recipes collection.

Deleted Recipes: Holds all recipe documents that have been deleted in the main application.


# Testing
All HTML and CSS has been run through the W3 validators and cleared of errors.

All pages have been tested on all screen sizes. This has been done via Google Chrome
developer tools and by testing on my own personal phone and ipad.

All of the actions below have been tested on multiple browsers. These include Chrome, 
Safari, Edge, Firefox and Opera.

1. As a vegan, I would like to be able to search through a list of recipes based 
on their type, in  order to avoid going through all ingredient lists.
- From the home page, click "Browse all recipes"
- Click the next and prev buttons to view other pages.
- Try clicking 'Update Results' without selecting a filter option.
- Select one option and click 'Update Results'.
- View the recipe.
- Return to the 'Browse all Recipes' page by clicking the 'Back to results' button.
- Press the Reset button.
- Select two options to filter and click 'Update Results'.
- Note whether the results return all contain both of these categories.
- Repeat with all 3 filter options selected.

2. As a cook, I would like to be able to store any recipes I create, in order to 
access and share with others.
- From the home page, click Log In.
- In the login modal, click Create Account.
- Try entering a different password in the 'Re-enter Password' box.
- Enter correct details and click Create User.
- Click Log Out.
- Click Log In and Create Account again.
- Try to create a new account with the same user name.
- Close the modal and click Log In.
- Try to log in with a username that doesn't exist.
- Try to log in with an incorrect password.
- Log in with the correct credentials and click Add Recipe.
- Try submitting the form empty.
- Enter details for the recipe. Use add and remove buttons on Ingredients and Method.
- Try uploading a file that is not an image.
- Try uploading an image file.
- Submit the form.
- Click Edit recipe.
- Click Submit without changing any details.
- Go back to edit screen and remove all details, submit.
- Fill in all details correctly and submit.
- Go to home page and enter the name of the recipe into the search field.
- In the results, click All Recipes
- In the list, click the recipe to open its page.
- Filter the browsing results by that recipe's category to ensure it appears.
- Open the recipe page and click Delete Recipe.
- Try entering incorrect credentials.
- Enter correct credentials.
- Check search and browse results to see if the recipe is now removed.

##### Testing Category Add/Delete
- Login to the app.
- Click Manage and then Categories from the drop down list.
- Try submitting a new category without selecting a heading.
- Try submitting a new category with a heading but no name.
- Submit a new category with a heading and a name.
- Click Manage > Add Recipe.
- Scroll down to categories to see the new category in the applicable list.
- Go back to Manage > Categories.
- Click Delete without selecting a category.
- Select the category you have just created and click Delete.


##### Testing Rating/Logged in access
- Log out of the app.
- Go to a recipe page for an unrated recipe and try to rate/edit/delete the recipe.
- Log in.
- Observe whether these options are now available.
- Give the recipe a rating of 5.
- Observe whether this rating appears.
- Observe whether rating again is an option.
- Log in with a different user account and give the recipe a rating of 1.
- Observe whether the rating has now changed.

##### Testing Error Handlers
- Try going to https://online-cookbook-hev.herokuapp.com/nonexistentpage and 
observe the custom 404 error.
- Click the image to ensure the link is active.
- On the add_recipe page, try uploading a file that is not an image and check the 
custom 500 page.
- Click the button to go back to the previous page.

### Bugs

###### Images issue
The current setup for uploading images to the website uses flask-upload and involves
the image selected by the user to be uploaded to static/img/uploads. This will work 
as long as the app is running all the time.

Because of the nature of heroku, where the app is currently live, the current
setup for images uploaded onto the website means that once the application stops 
running, any images that a user has uploaded when adding new recipes will be 
deleted. There are various ways around this,it could be possible to use an AWS 
S3 bucket and have the images hosted there rather than the current setup of 
pushing them to a folder in the site's directory.The workaround I have settled on 
is to use the `onerror` attribute of the html `img` tag to point to an alternative 
filepath if the requested image is not found. This means that uploaded images on 
heroku will not remain permanently, but when they are deleted they will be replaced
with a backup image which avoids broken image links.

##### Caching
There appear to be some caching issues with the adding and deleting of categories.
The newly added category will not appear in the list of categories available to delete
without restarting the app, and then will not disappear after deletion, again without 
restarting the app. The data is being updated in the database so these functions 
are definitely working as intended, but the cached information is not always being 
cleared.

# Deployment

The application is currently hosted live on Heroku; the code in the live version 
is identical to that here on github.

It can be installed with the following steps:
1. Download the git repository
2. Sign up/login to Heroku.com
3. From the dashboard click Create New App
4. Enter a unique name and your region and click Create
5. From your command line, enter `heroku` to ensure heroku is installed (if not 
installed this can be done with `sudo snap install --classic heroku`)
6. CLI: `heroku login`
7. Enter your credentials for heroku.com
8. CLI: `sudo pip3 install Flask`
9. CLI: `sudo pip3 install pymongo`
10. CLI: `sudo pip3 freeze --local > requirements.txt`
11. CLI: `echo web: python run.py > Procfile`
12. CLI: `git add .`
13. CLI: `git commit -m "initial deployment"`
14. CLI: `git push -u heroku master`
15. CLI: `heroku ps:scale web=1`
16. From heroku.com app settings: set config vars to IP : 0.0.0.0, PORT : 5000 and 
MONGO_URI : `mongodb://<dbuser>:<dbpassword>@ds253203.mlab.com:53203/online_cookbook`, 
ensuring that you update the username and password accordingly.
17. Click More > Restart all Dynos
18. App should now be live at https://your-app-name.herokuapp.com/

# Credits
## Content
All recipes on this website are credited to the author accordingly. Most are from 
the bbc.com food website with some coming from recipe books. All details are indicated
where necessary.


## Media
All images are from free image websites including www.freeimages.com, www.shutterstock.com
and https://pxhere.com.
The favicon is from https://www.freefavicon.com


## Acknowledgements
This project was based on a brief written by Code Institute to fulfil requirements 
of their Data Centric Development module (part of the Full Stack Web Developer course).

 I found the [Pretty Printed](https://www.youtube.com/channel/UC-QDfvrRIDB6F0bIO4I4HkQ)
 YouTube channel a huge help in learning about Flask sessions and error handling.
 
 Many thanks also to Chris Zielinski who is my Code Institute mentor, for offering 
 ideas and solutions to various issues throughout the project, as well as endless 
 patience and understanding!

