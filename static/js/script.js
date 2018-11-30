$(document).ready(function() {
    $('.sidenav').sidenav(); //Materializecss.com navigation bar
    $('select').formSelect(); //Materializecss.com select elements in forms
    $('.modal').modal(); //Materializecss.com modal for login

    //Button to add next ingredient on add recipe page
    var ing_count = 1;
    $('#add_ingredient').on('click', function() {
        var new_ingredient = `<div class="row ingredient">
                                    <div class="input-field col s6 offset-s3">
                                        <input id="ing" type="text" name="ingredients" placeholder="Enter Ingredient" class="validate">
                                    </div>
                            </div>`;
        $(new_ingredient).hide().appendTo("#ingredients_container").fadeIn(300);
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

    //Reveal remove button on edit_recipe.html
    $('.edit_new_ingredient').on('click', function() {
        $('#remove_ing_button').removeClass('hidden');
    });


    //Button to remove ingredient on edit_recipe.html
    var ing_count_edit = $('.ingredient').length //counts the number of ingredients already on the page
    $('.remove_current_ingredient').on('click', function() {
        $(this).closest(".ingredient").fadeOut(300).remove();
        ing_count_edit--;
    });


    //Button to add next step for method on add_recipe.html
    var step_count = 2; //must start from 2 as id=1 is already used on add_recipe.html form for the first method
    $('#add_method').on('click', function() {
        var new_method = `<div class="row method">
                                <div class="input-field col s12">
                                    <li><textarea type="text" class="validate" name="` + step_count + `" placeholder="Enter step ` + step_count + `"></textarea></li>
                                </div>
                            </div>`;
        $(new_method).hide().appendTo("#method_container ol").fadeIn(300);
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


    var step_count_edit = $('#method_container ol li').length + 1
    $('#add_method_to_existing').on('click', function() {
        var new_method_to_existing = `<div class="row method">
                                        <div class="input-field col s12">
                                            <li><textarea type="text" class="validate" name="` + step_count_edit + `" placeholder="Enter step ` + step_count_edit + `"></textarea></li>
                                        </div>
                                    </div>`;
        $(new_method_to_existing).hide().appendTo('#method_container ol').fadeIn(300);
        step_count_edit++;
    });

    $('#remove_step_from_existing').on('click', function() {
        if (step_count_edit > 2) {
            $('.method').last().fadeOut(300).remove();
            step_count_edit--;
        }
        if (step_count_edit == 2) {
            $('#remove_step_from_existing').addClass('hidden');
        }

    });

    $('#login-form').submit(function(e) {
        e.preventDefault();
        console.log("click");
        if (!$('input[name="username"]').val()) {
            $("#errors-here").text("Please enter a username")
        }
        else {
            $.get('/login', {
                u: $('input[name="username"]').val(),
                p: $('input[name="password"]').val()
            }, function(data) {
                if (data == "You were successfully logged in") {
                    $("#errors-here").text(data);
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                }
                $("#errors-here").text(data);
            });
            return false;
        }
    });

    $('#create-new-user').submit(function(e) {
        e.preventDefault();
        console.log('click');
        console.log($('input[name="newpassword"]').val())
        console.log($('input[name="repeatpassword"]').val())
        if (!$('input[name="newusername"]').val()) {
            $("#new-errors-here").text("Please enter a username");
        }
        else {
            console.log("username ok");
        }
        if ($('input[name="newpassword"]').val() != $('input[name="repeatpassword"]').val()) {
            $("#new-errors-here").text("Passwords don't match");
        }
        else {
            console.log("password ok");
            $.get('/create_user', {
                u: $('input[name="newusername"]').val(),
                p: $('input[name="newpassword"]').val()
            }, function(data) {
                console.log(data);
                if (data == "User created, you will now be logged in") {
                    $("#new-errors-here").text(data);
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                }
                $("#new-errors-here").text(data);
            });
            return false;
        }
    });
    


});
