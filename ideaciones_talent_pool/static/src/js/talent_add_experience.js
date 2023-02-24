odoo.define('ideaciones_talent_pool.experience.add', function (require) {
    'use strict';

    var core = require('web.core');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var publicWidget = require('web.public.widget');
    var rpc = require("web.rpc");
    var QWeb = core.qweb;
    var _t = core._t;

    var ExperienceDialog = Dialog.extend({
        template: 'website.talent.experience.add',
        events: _.extend({}, Dialog.prototype.events, {
            //'change input#tag_id' : '_onChangeTag',
        }),

        //settings all the values needed in frontend
        willStart: function () {
            var self = this;
            // Specialties res.partner.specialty
            var def_specialty = rpc.query({
                model: 'res.partner.specialty',
                method: 'search_read',
                args: [
                    [],
                    ['id', 'name'],
                ],
            }).then(function (res) {
                self.def_specialty = res;
            });
            // The Categories cv.experience.category
            var def_category = rpc.query({
                model: 'cv.experience.category',
                method: 'search_read',
                args: [
                    [],
                    ['id', 'name'],
                ],
            }).then(function (res) {
                self.def_category = {};
                $.each(res, function (i, field) {
                    self.def_category[field.id] = field.name;
                });
            });
            // The Countries
            var def_country = rpc.query({
                model: 'res.country',
                method: 'search_read',
                args: [
                    [],
                    ['id', 'name'],
                ],
            }).then(function (res) {
                self.def_country = {};
                $.each(res, function (i, field) {
                    self.def_country[field.id] = field.name;
                });
            });
            return Promise.all(
            [
                def_specialty,
                def_country,
                def_category,
                this._super.apply(this, arguments)
            ]);
        },

        /**
         * @override
         * @param {Object} parent
         * @param {Object} options holding channelId
         *
         */
        init: function (parent, options) {
            this.mode = options['mode'];
            this.category_type = options['category_type'] || false;
            this.name = options['name'] || false;
            this.role_function = options['role_function'] || false;
            this.experience_id = options['experience_id'] || false;
            this.period = options['period'] || false;
            this.institution = options['institution'] || false;
            this.duration = options['duration'] || false;
            this.qty_credits = options['qty_credits'] || false;
            this.description = options['description'] || false;
            this.country_id = options['country_id'] || false;
            this.category_id = options['category_id'] || false;
            var experience_dialog_mode_values = this._get_experience_dialog_mode_values(options);

            options = _.defaults(options || {}, {
                title: experience_dialog_mode_values['title'],
                size: 'medium',
                buttons: [{
                    text: experience_dialog_mode_values['text'],
                    classes: 'btn-primary',
                    click: this._onClickFormSubmit.bind(this)
                }, {
                    text: _t("Cancelar"),
                    click: this._onClickClose.bind(this)
                }]
            });

            this._super(parent, options);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        /**
         * @private
         */

        _get_experience_dialog_mode_values(options) {
            if(options['mode'] == 'update'){
                return {'title': _t("Actualizar Experiencia"), 'text': _t("Update")};
            }else{
                return  {'title': _t("Añadir Experiencia"), 'text': _t("Add")};
            }
        },
        _formValidate: function ($form) {
            $form.addClass('was-validated');
            var result = $form[0].checkValidity();
            return result;
        },

        _alertDisplay: function (message) {
            this._alertRemove();
            $('<div/>', {
                "class": 'alert alert-warning',
                role: 'alert'
            }).text(message).insertBefore(this.$('form'));
        },
        _alertRemove: function () {
            this.$('.alert-warning').remove();
        },

        //--------------------------------------------------------------------------
        // Handler
        //--------------------------------------------------------------------------

        _extract_form_submit_values: function ($form) {
            var values = {};
            $.each($form.serializeArray(), function (i, field) {
                values[field.name] = field.value;
            });
            return values;
        },
        _get_operation_url: function(){
            if(this.mode == 'update'){
                return '/ideaciones/update/experience';
            }
            return '/ideaciones/add/experience';
        },

        _onClickFormSubmit: function (ev) {
            var self = this;
            var $form = $(this.$el[0].firstElementChild);
            var data = this._extract_form_submit_values($form);
            if(this.mode == 'update'){
                data['experience_id'] = this.experience_id;
                data['mode'] = 'update';
            }
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: self._get_operation_url(),
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": data}),
                success: function (result) {
                    data['experience_id'] = result['result']['experience_id'];
                    core.bus.trigger('update_experience', data);
                    self._onClickClose();
                },
                error: function (data) {
                    console.error("ERROR ", data);
                },
            });
        },
        _onClickClose: function () {
            this.close();
        },
    });

    publicWidget.registry.websiteTalentExperience = publicWidget.Widget.extend({
        selector: '.o_wtalent_js_add_experience',
        xmlDependencies: ['/ideaciones_talent_pool/static/src/xml/website_talent_experience.xml'],
        events: {
            'click': 'onAddExperienceClick',
        },
        custom_events: _.extend({}, publicWidget.Widget.prototype.custom_events, {
            'close_modal_experience': '_on_close_modal_experience',
        }),

        init: function (parent, data) {
            this._super(parent, data);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _openDialog: function ($element,category_type) {
            var data = $element.data();
            // alert(category_type);
            return new ExperienceDialog(this, {"category_type":category_type}).open();
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        onAddExperienceClick: function (ev) {
            ev.preventDefault();
            var category_type = $(ev.currentTarget).attr('aria-label');
            this._openDialog($(ev.currentTarget),category_type);
        },
    });

    var ExperienceWidgetRow = publicWidget.Widget.extend({
        template: 'experience_row',
        xmlDependencies: ['/ideaciones_talent_pool/static/src/xml/website_talent_experience.xml'],

        init: function (data) {
            this._super(data);
            this.experience_id = data['experience_id'];
            this.category_id = data['category_id'];
            this.name = data['name'];
            this.period = data['period'];
        },
    });

    var ExperienceWidget = publicWidget.Widget.extend({
        template: 'add_experience_to_cv',
        xmlDependencies: ['/ideaciones_talent_pool/static/src/xml/website_talent_experience.xml'],
        events: {
            'click .delete-experience': '_on_delete_experience',
            'click .update-experience': '_on_update_experience',
        },
        //settings all the values needed in frontend
        willStart: function () {
            var self = this;
            var args = [
                [['user_ids', 'in', session.user_id]],
                ['id','name', 'period','category_id'],
            ];
            var def_xp = rpc.query({
                model: 'res.partner.experience.line',
                method: 'search_read',
                args: args,
            }).then(function (res) {
                self.experience_ids = res;
            });
            return Promise.all(
            [
                def_xp,this._super.apply(this, arguments)
            ]);
        },

        start: function () {
            var self = this;
            core.bus.on('update_experience', this, this._update_experience);
            for (var experience of this.experience_ids) {
                self._update_experience({
                    'experience_id': experience['id'],
                    'name': experience['name'],
                    'period': experience['period'],
                    'category_id': experience['category_id'],
                })
            }
            return this._super.apply(this, arguments);
        },
        _update_experience: function (data) {
            var values = {
                    'experience_id': data['experience_id'],
                    'name': data['name'],
                    'period': data['period'],
                    'category_id': data['category_id'],
            };
            var new_row = new ExperienceWidgetRow(values);
            if(data['mode'] == 'update'){
                this.$el.find("[name-id='" + values['experience_id'] + "']").replaceWith(QWeb.render('experience_row', {'widget': new_row}));
            }else{
                new_row.appendTo(this.$el.find("tbody"));
            }
        },
        _on_update_experience: function(ev) {
            var experience_id = $(ev.target).closest('tr').attr('name-id');
            var data = {
                "experience_id": experience_id
            };
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: '/ideaciones/get_experiences_modal_values',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": data}),
                success: function (result) {
                    var dialog_values = {'mode': 'update'};
                    _.extend(dialog_values, result['result'], data);
                    return new ExperienceDialog(this, dialog_values).open();
                },
                error: function (data) {
                    console.error("ERROR ", data);
                },
            });

        },
        _on_delete_experience: function (ev) {
            var self = this;
            var experience_id = $(ev.target).closest('tr').attr('name-id');
            var data = {
                'experience_id': experience_id
            };

            $.ajax({
                type: "POST",
                dataType: 'json',
                url: '/ideaciones/delete/experience',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": data}),
                success: function (result) {
                    self.$el.find("[name-id='" + experience_id + "']").remove();
                },
                error: function (data) {
                    console.error("ERROR ", data);
                },
            });
        },
    });

    $(document).ready(function () {
        setTimeout(function () {
            var $elem = $('#ideaciones_experiences');
            if ($elem.length > 0) {
                var app = new ExperienceWidget(null);
                app.prependTo($elem);
            }
        }, 700);
    });

    return {
        ExperienceDialog: ExperienceDialog,
        websiteTalentExperience: publicWidget.registry.websiteTalentExperience
    };

});
