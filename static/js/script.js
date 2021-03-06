$(document).ready(function() {
    $('.sidenav').sidenav(); //Materializecss.com navigation bar
    $('select').formSelect(); //Materializecss.com select elements in forms
    $('.modal').modal(); //Materializecss.com modal for login
    $('.collapsible').collapsible(); //Materializecss.com collapsible elements for mobile view
    $('.dropdown-trigger').dropdown(); //materializecss.com dropdown menu (navbar)
    

    //Button to add next ingredient on add recipe page
    var ing_count = 1;
    $('#add_ingredient').on('click', function() {
        //check to see which page is being used before assigning the variable:
        //this button appears on both add_recipe.html and edit_recipe.html but the 
        //html varies slightly on each page.
        if ($('.page-title').text() == 'Add a Recipe') {
            var new_ingredient = `<div class="col s12 input-field ingredient white-background z-depth-2">
                                <input id="ing" type="text" name="ingredients" placeholder="Next ingredient..." class="validate" required>
                        </div>`;
        }
        else {
            new_ingredient = `<div class="row">
                                    <div class="col s12 input-field ingredient white-background z-depth-2">
                                        <input id="ing" type="text" name="ingredients" placeholder="Next ingredient..." class="validate" required>
                                    </div>
                                </div>`;
        }
        $(new_ingredient).hide().appendTo("#ingredients_container").fadeIn(300);
        //the remove button should not be available if there are no elements to 
        //remove
        if (ing_count > 0) {
            $('#remove_ing_button').removeClass('hidden');
        }

        ing_count++;

    });


    //Button to remove ingredient on add_recipe.html
    $('#remove_ingredient').on('click', function() {
        if (ing_count > 1) {
            $('.ingredient').last().fadeOut(300).remove();
            ing_count--;
        }
        if (ing_count == 1) {
            $('#remove_ing_button').addClass('hidden');
        }
    });


    //Button to remove single ingredient on edit_recipe.html
    $('.remove_current_ingredient').on('click', function() {
        $(this).parent().fadeOut(300).remove();
    });


    //Button to add next step for method on add_recipe.html
    var step_count = 2; //must start from 2 as id=01 is already used on add_recipe.html form for the first method

    $('#add_method').on('click', function() {
        //Adds zeros to all numbers below 10 so that method appears alphabetically on recipe page
        if (step_count < 10) {
            var zero = "0";
        }
        else {
            zero = "";
        }
        var new_method = `<div class="col s12 input-field method white-background z-depth-2">
                                <textarea class="materialize-textarea" name="` + zero + step_count + `" placeholder="Enter step ` + step_count + `" required></textarea>
                                </div>
                            </div>`;
        $(new_method).hide().appendTo("#method_container").fadeIn(300);
        if (step_count > 1) {
            $('#remove_step_button').removeClass('hidden');
        }
        step_count++;

    });
    //Button to remove method step on add_recipe.html
    $('#remove_step').on('click', function() {
        if (step_count > 2) {
            $('.method').last().fadeOut(300).remove();
            step_count--;
        }
        if (step_count == 2) {
            $('#remove_step_button').addClass('hidden');
        }
    });

    //the edit page requires a different count when adding steps due to already having the current recipe's steps counted
    var step_count_edit = $('#method_container .method').length + 1;

    $('#add_method_to_existing').on('click', function() {
        if (step_count_edit > 1) {
            $('#remove_step_from_existing').removeClass('hidden');
        }
        var new_method_to_existing = `<div class="col s12 input-field method white-background z-depth-2">
                                        <textarea class="materialize-textarea" name="` + step_count_edit + `" placeholder="Enter step ` + step_count_edit + `"></textarea>
                                    </div>`;

        $(new_method_to_existing).hide().appendTo('#method_container').fadeIn(300);
        step_count_edit++;
    });

    //Button to remove step from method in edit_recipe.html
    $('#remove_step_from_existing').on('click', function() {
        if (step_count_edit > 2) {
            $('.method').last().fadeOut(300).remove();
            step_count_edit--;
        }
        if (step_count_edit == 2) {
            $('#remove_step_from_existing').addClass('hidden');
        }

    });

    //On submit of login modal: triggers the run.py login function and appends the returned message to the relevant div.
    $('#login-form').submit(function(e) {
        e.preventDefault();
        if (!$('input[name="username"]').val()) {
            $("#errors-here").text("Please enter a username");
        }
        else {
            $.get('/login', {
                u: $('input[name="username"]').val(),
                p: $('input[name="password"]').val()
            }, function(data) {
                if (data == "You were successfully logged in") {
                    $("#errors-here").text(data);
                    $('#loader').removeClass('no-display');
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                }
                $("#errors-here").text(data);
            });
            return false;
        }
    });


    //On submit of new user modal: triggers the run.py create_user function and appends the returned message to the relevant div.
    $('#create-new-user').submit(function(e) {
        e.preventDefault();
        if (!$('input[name="newusername"]').val()) {
            $("#new-errors-here").text("Please enter a username");
        }
        if ($('input[name="newpassword"]').val() != $('input[name="repeatpassword"]').val()) {
            $("#new-errors-here").text("Passwords don't match");
        }
        else {
            $.get('/create_user', {
                u: $('input[name="newusername"]').val(),
                p: $('input[name="newpassword"]').val()
            }, function(data) {
                if (data == "User created, you will now be logged in") {
                    $("#new-errors-here").text(data);
                    $('#new-user-loader').removeClass('no-display');
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                }
                $("#new-errors-here").text(data);
            });
            return false;
        }
    });

    //On submit of delete recipe modal: triggers the run.py delete_recipe function and appends the returned message to the relevant div.
    $('#delete-recipe').submit(function(e) {
        e.preventDefault();
        if (!$('input[name="user-deleting"]').val()) {
            $("#delete-errors-here").text("Please enter a username");
        }
        var recipe_id = $('input[name="recipe-id"]').val();
        $.get('/delete_recipe', {
            user: $('input[name="user-deleting"]').val(),
            password: $('input[name="password-to-delete"]').val(),
            recipe_id: recipe_id
        }, function(data) {
            if (data == "Recipe Deleted") {
                $("#delete-errors-here").text(data);
                $('#delete-recipe-loader').removeClass('no-display');
                setTimeout(function() {
                    window.location = ('/');
                }, 2000);
            }
            $("#delete-errors-here").text(data);
        });
        return false;

    });


    $('#backToResults').click(function() {
        parent.history.back();
        return false;
    });
    
    var lastPageVisited = document.referrer.toString();
  
    if (lastPageVisited.indexOf("get_recipes") > -1 || lastPageVisited.indexOf("search") > -1) {
        $('#back-to-results').removeClass('no-display');
    }
});
