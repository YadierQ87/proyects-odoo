odoo.define('ideaciones_talent_pool.skill.add', function (require) {
    'use strict';

    var core = require('web.core');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var publicWidget = require('web.public.widget');
    var rpc = require("web.rpc");
    var QWeb = core.qweb;
    var _t = core._t;

    var SkillDialog = Dialog.extend({
        template: 'website.talent.skill.add',
        events: _.extend({}, Dialog.prototype.events, {
            //'change input#tag_id' : '_onChangeTag',
        }),

        /**
         * @override
         * @param {Object} parent
         * @param {Object} options holding channelId
         *
         */
        init: function (parent, options) {
            this.mode = options['mode'];
            this.specialty = options['specialty'] || false;
            this.skills_ids = options['skills_ids'] || false;
            this.competence_id = options['competence_id'] || false;
            var skill_dialog_mode_values = this._get_skill_dialog_mode_values(options);
            options = _.defaults(options || {}, {
                title: skill_dialog_mode_values['title'],
                size: 'medium',
                buttons: [{
                    text: skill_dialog_mode_values['text'],
                    classes: 'btn-primary',
                    click: this._onClickFormSubmit.bind(this)
                }, {
                    text: _t("Discard"),
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

        _get_skill_dialog_mode_values(options) {
            if(options['mode'] == 'update'){
                return {'title': _t("Actualizar Competencia"), 'text': _t("Update")};
            }else{
                return  {'title': _t("Añadir Competencia"), 'text': _t("Add")};
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
                return '/ideaciones/update/skill';
            }
            return '/ideaciones/add/skill';
        },

        _onClickFormSubmit: function (ev) {
            var self = this;
            var $form = $(this.$el[0].firstElementChild);
            var data = this._extract_form_submit_values($form);
            if(this.mode == 'update'){
                data['competence_id'] = this.competence_id;
                data['mode'] = 'update';
            }
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: self._get_operation_url(),
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": data}),
                success: function (result) {
                    data['competence_id'] = result['result']['competence_id'];
                    core.bus.trigger('update_competence', data);
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

    publicWidget.registry.websiteTalentSkill = publicWidget.Widget.extend({
        selector: '.o_wtalent_js_add_skill',
        xmlDependencies: ['/ideaciones_talent_pool/static/src/xml/website_talent_skill.xml'],
        events: {
            'click': 'onAddSkillClick',
        },
        custom_events: _.extend({}, publicWidget.Widget.prototype.custom_events, {
            'close_modal_skill': '_on_close_modal_skill',
        }),

        init: function (parent, data) {
            this._super(parent, data);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _openDialog: function ($element) {
            var data = $element.data();
            return new SkillDialog(this, {}).open();
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        onAddSkillClick: function (ev) {
            ev.preventDefault();
            this._openDialog($(ev.currentTarget));
        },
    });

    var SkillWidgetRow = publicWidget.Widget.extend({
        template: 'skill_row',
        xmlDependencies: ['/ideaciones_talent_pool/static/src/xml/website_talent_skill.xml'],

        init: function (data) {
            this._super(data);
            this.competence_id = data['competence_id'];
            this.specialty = data['specialty'];
            this.skill = data['skill'];
            self.competence_ids = null;
        },
    });

    var SkillWidget = publicWidget.Widget.extend({
        template: 'add_skill_to_cv',
        xmlDependencies: ['/ideaciones_talent_pool/static/src/xml/website_talent_skill.xml'],
        events: {
            'click .delete-skill': '_on_delete_competence',
            'click .update-skill': '_on_update_compentence',
        },

        willStart: function () {
            var self = this;
            var args = [
                [['user_ids', 'in', session.user_id]],
                ['id', 'specialty', 'skills_ids'],
            ];
            var def_skills = rpc.query({
                model: 'res.partner.skill',
                method: 'search_read',
                args: [
                    [],
                    ['id', 'name'],
                ],
            }).then(function (res) {
                self.skill_names = {};
                $.each(res, function (i, field) {
                    self.skill_names[field.id] = field.name;
                });


            });
            var def = rpc.query({
                model: 'res.partner.competences',
                method: 'search_read',
                args: args,

            }).then(function (res) {
                self.competence_ids = res;
            });

            return Promise.all([def_skills, def, this._super.apply(this, arguments)]);
        },

        start: function () {
            var self = this;
            core.bus.on('update_competence', this, this._update_competence);
            for (var competence of this.competence_ids) {
                self._update_competence({
                    'competence_id': competence['id'],
                    'tag_id': competence['specialty'][1],
                    'tag_group_id': _.map(competence['skills_ids'], function (val) {
                        return self.skill_names[val]
                    }).join(','),
                })
            }
            return this._super.apply(this, arguments);
        },
        _update_competence: function (data) {
            var values = {
                'specialty': data['tag_id'],
                'skill': data['tag_group_id'],
                'competence_id': data['competence_id']
            };
            var new_row = new SkillWidgetRow(values);
            if(data['mode'] == 'update'){
                this.$el.find("[competence-id='" + values['competence_id'] + "']").replaceWith(QWeb.render('skill_row', {'widget': new_row}));
            }else{
                new_row.appendTo(this.$el.find("tbody"));
            }
        },
        _on_update_compentence: function(ev) {
            var competence_id = $(ev.target).closest('tr').attr('competence-id');
            var data = {
                "competence_id": competence_id
            };
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: '/ideaciones/get_skills_modal_values',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": data}),
                success: function (result) {
                    var dialog_values = {'mode': 'update'};
                    _.extend(dialog_values, result['result'], data);
                    return new SkillDialog(this, dialog_values).open();
                },
                error: function (data) {
                    console.error("ERROR ", data);
                },
            });

        },
        _on_delete_competence: function (ev) {
            var self = this;
            var competence_id = $(ev.target).closest('tr').attr('competence-id');
            var data = {
                'competence_id': competence_id
            };

            $.ajax({
                type: "POST",
                dataType: 'json',
                url: '/ideaciones/delete/skill',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": data}),
                success: function (result) {
                    self.$el.find("[competence-id='" + competence_id + "']").remove();
                },
                error: function (data) {
                    console.error("ERROR ", data);
                },
            });
        },
    });

    $(document).ready(function () {
        setTimeout(function () {
            var $elem = $('#ideaciones_skills');
            if ($elem.length > 0) {
                var app = new SkillWidget(null);
                app.prependTo($elem);
            }
        }, 700);
    });

    return {
        SkillDialog: SkillDialog,
        websiteTalentSkill: publicWidget.registry.websiteTalentSkill
    };

});
