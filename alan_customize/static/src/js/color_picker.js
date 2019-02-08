odoo.define('alan_customize.color_picker_js', function(require){
    var ignoreReadyState = true;
    function rgb2hex(rgb) {
        rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
        function hex(x) {
            return ("0" + parseInt(x).toString(16)).slice(-2);
        }
        return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
    }
    $(document).ready(function(){
        $("#theme_customize").on("click", function(){
            ignoreReadyState = true;
            $(document).on("focus", "#theme_customize_modal", function(){
                $("input#color_picker_radio").css("display", "none");
                var current_color = $("#color_picker_button").css("background-color").toLowerCase();
                if(current_color.indexOf('#') == -1)
                    current_color = rgb2hex(current_color);
                $("#color_picker").val(current_color);
                $("color_picker").trigger("change");
            });
            $(document).on("blur", "#theme_customize_modal", function(){
                $(document).off("focus", "#theme_customize_modal");
            });
        });
    });
    $(document).on("change", "input[type=radio][name=colorvar]", function(){
        if($("input[type=radio][name=colorvar]:checked").val() == 'color_picker_value'){
            if(ignoreReadyState)
                ignoreReadyState = false;
            else{
                var chosen_color = $("#color_picker").val().toLowerCase();
                if(chosen_color){
                    var filePath = "/static/src/scss/options/colors/color_picker.scss";
                    var replacing_color_str = "@as-theme:\t\t\t\t" + chosen_color + ";";
                    $.get("/update_scss_file", {
                        'file_path': filePath, 'write_str': replacing_color_str
                    });
                }
            }
        }
    });
    $(document).on("click", "#color_picker_button", function(){
        $("input#color_picker_radio").prop("checked", "true");
        $("input[type=radio][name=colorvar]").trigger("change");
        $("#color_picker").trigger("change");
    });
    $(document).on("change", "#color_picker", function(){
        var chosen_color = $(this).val().toLowerCase();
        var current_color = $("#color_picker_button").css("background-color").toLowerCase();
        if(current_color.indexOf('#') == -1)
            current_color = rgb2hex(current_color);
        if(current_color.split("#")[1] === chosen_color.split("#")[1])
            $("#color_picker_button").prop("disabled", true);
        else
            $("#color_picker_button").prop("disabled", false);
    });
});