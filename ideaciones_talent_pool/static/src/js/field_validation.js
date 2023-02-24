odoo.define("ideaciones_talent_pool.field_validation", function (require) {
    "use strict";

    require("web.dom_ready");
    var Class = require("web.Class");
    var rpc = require("web.rpc");

    var personal_info_form = $(".js_update_personal_info");
//    if (!personal_info_form.length) {
//        return Promise.reject("DOM doesn't contain '.js_update_personal_info'");
//    }

    var submit_controller = personal_info_form.attr("action");

    $(".js_update_personal_info").on("submit", function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url: submit_controller,
            type: "POST",
            dataType: "json",
            beforeSubmit: function (formData, $form, options) {
                for (var i in formData) {
                    var $element = $form.find("#" + formData[i].name);
                    if ($element.length) {
                        var attr = $element.attr("validator-type");
                        if (typeof attr !== "undefined" && attr !== false) {
                            formData[i].name = attr + "#()#" + formData[i].name;
                        }
                    }
                }
                $(".js_errzone").html("").hide();
            },
            success: function (response, status, xhr) {
                if (_.has(response, "errors")) {
                    _.each(_.keys(response.errors), function (key) {
                        $("#" + key)
                            .siblings(".js_errzone")
                            .append("<p>" + response.errors[key] + "</p>")
                            .show();
                    });
                    return false;
                }
                window.location = "/contactus-talent-thank-you";
            },
            timeout: 5000,
        });
    });

    var FrontFieldValidatorBuilder = Class.extend({
        init: function () {
            this._validators = {};
        },
        register_validator: function (key, builder) {
            this._validators[key] = builder;
        },
        get_validator: function (key) {
            return this._validators[key];
        },
    });
    var UrlValidator = Class.extend({
        validate: function (term) {
            if (this.validURL(term) == false) {
                return {
                    error: "URL incorrecta",
                };
            }
            return {};
        },
        validURL: function (str) {
            var pattern = new RegExp(
                "^(https?:\\/\\/)?" + // Protocol
          "((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|" + // Domain name
          "((\\d{1,3}\\.){3}\\d{1,3}))" + // OR ip (v4) address
          "(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*" + // Port and path
          "(\\?[;&a-z\\d%_.~+=-]*)?" + // Query string
          "(\\#[-a-z\\d_]*)?$",
                "i"
            ); // Fragment locator
            return Boolean(pattern.test(str));
        },
    });
    var EmailValidator = Class.extend({
        validate: function (term) {
            const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            if (re.test(term) == false) {
                return {
                    error: "Email incorrecto",
                };
            }
            return {};
        },
    });
    var AlphanumericWithSpacesValidator = Class.extend({
        validate: function (term) {
            const re = /^[A-Za-z\d\s]+$/;
            if (re.test(term) == false) {
                return {
                    error: "El valor del campo no es válido.",
                };
            }
            return {};
        },
    });
    var PhoneValidator = Class.extend({
        validate: async function (term) {
            var result = await rpc
                .query({
                    route: "/ideaciones/validate_phone",
                    params: {number: term},
                })
                .then(function (result) {
                    return result;
                });
            return result;
        },
    });
    var FacebookValidator = Class.extend({
        validate: function (term) {
            const re = /^(?:(?:http|https):\/\/)?(?:www\.)?facebook\.com\/([\w\.])+$/;
            if (re.test(term) == false) {
                return {error: "URL de perfil de facebook inválida"};
            }
            return {};
        },
    });
    var LinkedinValidator = Class.extend({
        validate: function (term) {
            const re = /^(?:(?:http|https):\/\/)?(?:www\.)?linkedin\.com\/([\w\.])+$/;
            if (re.test(term) == false) {
                return {error: "URL de perfil de linkedin inválida"};
            }
            return {};
        },
    });
    var CIValidator = Class.extend({
        validate: function (term) {
            const re = /^([\d]{11}$)/;
            if (re.test(term) == false) {
                return {error: "CI incorrecto"};
            }
            return {};
        },
    });
    var ORCIDValidator = Class.extend({
        validate: function (term) {
            const re = /^(?:(?:http|https):\/\/)?orcid\.org\/([\w\.])+$/;
            if (re.test(term) == false) {
                return {error: "URL de perfil orcid inválida"};
            }
            return {};
        },
    });
    var validator_builder = new FrontFieldValidatorBuilder();
    validator_builder.register_validator("validate_url", new UrlValidator());
    validator_builder.register_validator("validate_email", new EmailValidator());
    validator_builder.register_validator(
        "validate_alphanumeric_with_spaces",
        new AlphanumericWithSpacesValidator()
    );
    validator_builder.register_validator("validate_phone", new PhoneValidator());
    validator_builder.register_validator("validate_facebook", new FacebookValidator());
    validator_builder.register_validator("validate_linkedin", new LinkedinValidator());
    validator_builder.register_validator("validate_ci", new CIValidator());
    validator_builder.register_validator("validate_orcid", new ORCIDValidator());

    $("[validator-type]").focusout(function (ev) {
        var self = this;
        var validator = validator_builder.get_validator($(this).attr("validator-type"));
        var error_promise = validator.validate($(this).val());
        $(this).siblings(".js_errzone").html("");
        Promise.resolve(error_promise).then(function (error) {
            if (_.has(error, "error")) {
                $(self)
                    .siblings(".js_errzone")
                    .append("<p>" + error.error + "</p>")
                    .show();
            } else {
                $(self).siblings(".js_errzone").hide();
            }
        });
    });
});
