$(document).ready(function() {
    $('.sidenav').sidenav(); //Materializecss.com navigation bar
    $('select').formSelect(); //Materializecss.com select elements in forms
    
    //Button to add next ingredient on add recipe page
    var ing_count = 2 ;
    $('#add_ingredient').click(function() {
        $('#ingredients_container').append(`<div class="ingredient">
                                                <div class="input-field col s6">
                                                    <input id="ing_name_` + ing_count + `" placeholder="Enter ingredient ` + ing_count + `" type="text" name="ing_name_` + ing_count + `" class="validate">
                                                </div>
                                                <div class="input-field col s6">
                                                    <input id="ing_amount_` + ing_count + `" placeholder="Enter amount" type="text" name="ing_amount_` + ing_count + `" class="validate">
                                                </div>
                                            </div>`);
        ing_count ++;
                                    
    });
    
    //Button to add next step for method on add recipe page
    var step_count = 2 ;
    $('#add_method').click(function() {
        $('#method_container').append(`<div class="method">
                                            <div class="input-field col s12">
                                            <input id="method" placeholder="Enter step ` + step_count + `" type="text" name="step_desc_` + step_count + `" class="validate">
                                        </div>`);
        step_count ++;
                                    
    });
});