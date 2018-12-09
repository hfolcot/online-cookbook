images: www.freeimages.com, www.shutterstock.com
https://materializecss.com/navbar.html
jquery
https://www.youtube.com/watch?v=T1ZVyY1LWOg <- Pretty Printed dot com introduction to Flask sessions
favicon free from https://www.freefavicon.com


Issues outstanding:
Select element has the 'required' attribute on add_category.html but is not working
--override submit and validate manually with js

Adding category in the wrong place as you have to refresh the add recipe page for 
it to appear and you''d lose all your input
--move add button to recipe page? or two stage form input...

delete categories.

how to post static files with flask on heroku
images - amazon s3? flask...boto https://stackoverflow.com/questions/52342974/serve-static-files-in-flask-from-private-aws-s3-bucket
answer = onerror=this.src="https://media.istockphoto.com/photos/place-setting-picture-id513623454?s=2048x2048"!!!


multiple clicks on add category allows that many entries into the db

Issues overcome:
Categories only creating the first list requested instead of all 3. due to cursor 
being at end of collection and unable to iterate over data more than once.
solved by creating local variable of cursor data. alternatively by using cursor.rewind() 
after each call but this results in repeated calls to the database which can affect performance.



All pages run through html checker with no errors. -- and again 9/12/18



Features to implement:
original design for filtering the results was a list of checkboxes, using an ajax 
call in script.js. this was abandoned in favour of using select boxes and mongodb 
querying from the python files due to the amount of code necessary to achieve the desired
effect. ajax code can be seen in script.js commit for 29/11/18.

add fields to recipe document to keep track of who has made edits.

something to fill up the space on the homepage when viewed on larger mobile devices.

separate the add and edit forms into two or three separate pages






##deployment 
change app.config["MONGO_URI"] so that it is `os.getenv(MONGO_URI)` then add `MONGO_URI`
and `mongodb://<dbuser>:<dbpassword>@ds253203.mlab.com:53203/online_cookbook` as a 
key and value in heroku settings.

##differences
app.config['mongo_uri'] configured as above in live but not in deployment.