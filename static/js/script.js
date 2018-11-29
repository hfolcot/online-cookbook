$(document).ready(function() {
    $('.sidenav').sidenav(); //Materializecss.com navigation bar
    $('select').formSelect(); //Materializecss.com select elements in forms

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


    var resultsSection = document.getElementById("results");
    var filteredResults = [];

    $('.cat-checkbox').on('click', function() { //when the checkbox is clicked
        var filterBy = $(this).val(); //get the value of the checkbox
        var checkList = [];
        if ($(this).is(":checked")) { //if the checkbox has been checked
            console.log(filterBy);
            $.get("/filter_results/" + filterBy).done(function(data) { //get run.py to run the mongodb query with the checkbox value as a parameter
                var recipes = (JSON.parse(data)); //create a variable holding the results and parse to JSON
                //console.log(recipes);
                //console.log(filteredResults.length);
                if (filteredResults.length > 0) {
                    console.log(filteredResults);
                    console.log("filtered results has something in it");

                    filteredResults.forEach(function(key) {
                        //console.log(typeof key._id.$oid);
                        //console.log(key._id.$oid);
                        checkList.push(key._id.$oid); //push the id into a list of ids for future comparison
                        console.log("checklist");
                        console.log(checkList);
                    });
                    Object.keys(recipes).forEach(function(item) { 
                        //console.log(item);
                        //console.log(typeof item);
                        if (checkList.indexOf(item) != -1) { //if the recipe is already in the filtered results
                            console.log("match found"); //do nothing
                        }
                        else { //if recipe is not in the filtered results
                            filteredResults.push(recipes[item]); //stick it in the filtered results array
                        }

                    });

                }
                else {
                    console.log("this is what happens when filtered results == 0");
                    Object.keys(recipes).forEach(function(key) { //for each item in the recipes variable...
                        filteredResults.push(recipes[key]); //push the item into an array called filteredResults, which is currently empty

                    });
                }
                console.log(filteredResults);
                resultsSection.innerHTML = ``; //clear the html ready for the new results
                filteredResults.forEach(function(key) { //for each of the filtered results, write the html below.
                    resultsSection.innerHTML += `<div class="col s12 m3">
                                                    <div class="card" id=${key._id.$oid}>
                                                        <div class="card-image">
                                                            <img src=${key['image']}>
                                                        </div>
                                                     <div class="card-content">
                                                            <p>${key.name}</p>
                                                        </div>
                                                        <div class="card-action">
                                                            <a href="recipe/${key._id.$oid}">See this recipe</a>
                                                        </div>
                                                    </div>
                                                </div>`;
                });
            });






        }
        else { //if the checkbox is unchecked
            var filtersRemoved = [];
            var toFilterOut = [];
            $.get("/filter_results/" + filterBy).done(function(data) {
                var recipes = (JSON.parse(data)); //create a variable holding the results and parse to JSON
                Object.keys(recipes).forEach(function(item) {
                    toFilterOut.push(item);
                    console.log("toFilterOut")
                    console.log(toFilterOut);
                    console.log("filteredResults:")
                    console.log(filteredResults)
                });
                filteredResults.forEach(function(i) {
                    console.log("this is i._id.$oid")
                    console.log(i._id.$oid)
                     if (toFilterOut.indexOf(i._id.$oid) != -1) {
                         console.log("not this one")
                         console.log(i)
                     }
                     else {
                         filtersRemoved.push(i)
                     }
                })
                console.log("filtersRemoved:")
                console.log(filtersRemoved)
                
                
                filtersRemoved.forEach(function(key) { //for each of the filtered results, write the html below.
                    console.log("now creating a card")
                    resultsSection.innerHTML = ''
                    resultsSection.innerHTML += `<div class="col s12 m3">
                                                    <div class="card" id=${key._id.$oid}>
                                                        <div class="card-image">
                                                            <img src=${key['image']}>
                                                        </div>
                                                     <div class="card-content">
                                                            <p>${key.name}</p>
                                                        </div>
                                                        <div class="card-action">
                                                            <a href="recipe/${key._id.$oid}">See this recipe</a>
                                                        </div>
                                                    </div>
                                                </div>`;
                });
            });

        }

    });


});
