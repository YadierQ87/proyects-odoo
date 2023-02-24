$(document).ready(function () {
    update_progress();
    function update_progress() {
        var total = 0;
        var filled = 0;
        var form_field_list = $('.form-control,.form-control-file');
        form_field_list.each(function () {
            if($(this).attr("type") == "INPUT")
                console.log($(this).attr('type'));
            switch ($(this).prop('nodeName')) {
                case "INPUT":
                    switch ($(this).attr("type")) {
                        case "text":
                            if ($(this).val() != "") {
                                filled++;
                            }
                            total++;
                            break;
                        case "email":
                            var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                            if (re.test(String($(this).val()).toLowerCase())) {
                                filled++;
                            }
                            total++;
                            break;
                        case "number":
                            if ($.isNumeric($(this).val())) {
                                filled++;
                            }
                            total++;
                            break;
                        case "checkbox":
                            if ($(this).is(':checked')) {
                                filled++;
                            }
                            total++;
                            break;
                        case "radio":
                            if ($(this).is(':checked')) {
                                filled++;
                            }
                            total++;
                            break;
                        case "file":
                            if ($(this).get(0).files.length > 0) {
                                filled++;
                            }
                            total++;
                            break;
                    }
                    break;
                case "SELECT":
                    if ($(this).val() != "") {
                        filled++;
                    }
                    total++;
                    break;
                case "TEXTAREA":
                    if ($(this).val() != "") {
                        filled++;
                    }
                    total++;
                    break;

            }
        });
        console.log(filled);
        console.log(total);
        console.log(filled * 100 / total);
        var current_progress = parseInt(filled * 100 / total);
        $('.progress-bar').attr('aria-valuenow', current_progress).css('width', current_progress + '%');
        $('.s_progress_bar_text').text(current_progress.toString() + "% Completado");
    }

    $('.update_personal_info, .profesional_info, .update_cv').change(function () {
        update_progress();
    });
});