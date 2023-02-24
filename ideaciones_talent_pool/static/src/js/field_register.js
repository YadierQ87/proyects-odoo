odoo.define('ideaciones_theme.field.register', function (require) {
'use strict';

var core = require('web.core');
var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');
var _t = core._t;
var ajax = require('web.ajax');
const dom = require('web.dom');
var qweb = core.qweb;

      // button for create register in web/signup
      $("#continue-button").on("click", function (e) {
        e.preventDefault();
        var form_valid = true
        $('.login-form').find(':input').each(function () {
            var field = this;
            if (field.classList.contains('is-invalid')){
                field.classList.remove('is-invalid');
            }
            var s_required = field.getAttribute('required');
            if (field.value == "" && s_required){
                 field.classList.add('is-invalid');
                 form_valid = false;
            }
        });
        if (!form_valid){
            var message = _t(" Por favor, llene el formulario correctamente. ");
            $('#s_website_form_result').html(message);
            $('#s_website_form_result').addClass('is-invalid');
            return false;
        }
        $('.login-form').submit();
      });

     //checking all variables for input typing
     $(".check_keys_input").on("keypress", function (e) {
        var spanish = 'abcdefghijklmnopqrstuvwxyz'
        var vocals = ' áéíóúñ';
        var numeric = '0123456789';
        var letters = spanish.concat(vocals);
        var alphanumeric = letters.concat(numeric);
        var phone = numeric.concat('+')
        var email = spanish.concat(numeric,'@.')
        var website = spanish.concat(numeric,':/.')

        var validator = $(this).attr("field-type");
        var key = e.which;
        var alpha = String.fromCharCode(key).toLowerCase();
        //console.log(alpha);

        switch(validator) {
          case 'letter':
            if (letters.indexOf(alpha) == -1)
                e.preventDefault();
            break;
          case 'numeric':
            if (numeric.indexOf(alpha) == -1)
                e.preventDefault();
            break;
          case 'phone':
            if (phone.indexOf(alpha) == -1)
                e.preventDefault();
            break;
          case 'email':
            if (email.indexOf(alpha) == -1)
                e.preventDefault();
            break;
          case 'website':
            if (website.indexOf(alpha) == -1)
                e.preventDefault();
            break;
          default:
            if (alphanumeric.indexOf(alpha) == -1)
                e.preventDefault();
        }

     });

});
