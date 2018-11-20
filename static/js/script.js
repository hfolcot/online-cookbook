$(document).ready(function() {
    $('.sidenav').sidenav(); //Materializecss.com navigation bar
    $('select').formSelect(); //Materializecss.com select elements in forms
    
    //Button to add next ingredient on add recipe page
    var ing_count = 2 ;
    $('#add_ingredient').click(function() {
        $('#ingredients_container').append(`<div class="row ingredient">
                                                <div class="input-field col s6">
                                                    <input id="ing_` + ing_count + `" placeholder="Enter ingredient ` + ing_count + `" type="text" name="ing_` + ing_count + `" class="validate">
                                                </div>
                                                `);
        if(ing_count > 1) {
            $('#remove_ing_button').removeClass('hidden');
        }                                       
        ing_count ++;
                                    
    });
    //Button to remove ingredient on add recipe page
    $('#remove_ingredient').click(function() {
        if(ing_count > 2) {
            $('.ingredient').last().remove();
            ing_count --;
        }
    });
    
    //Button to add next step for method on add recipe page
    var step_count = 2 ;
    $('#add_method').click(function() {
        $('#method_container').append(`<div class="method">
                                            <div class="input-field col s12">
                                            <input id="step_no" type="hidden" name="step_no_` + step_count + `" value="` + step_count + `">
                                            <textarea id="method" placeholder="Enter step ` + step_count + `" type="text" name="step_desc_` + step_count + `" class="validate"></textarea>
                                        </div>`);
        if(step_count > 1) {
            $('#remove_step_button').removeClass('hidden');
        }                                
        step_count ++;
                                    
    });
    //Button to remove method step on add recipe page
    $('#remove_step_button').click(function() {
        if(step_count > 2) {
            $('.method').last().remove();
            step_count --;
        }
    });
});

    $('.remove_current_ingredient').click(function() {
        $('.ingredient').last().remove();
    })