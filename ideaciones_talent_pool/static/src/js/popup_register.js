odoo.define('ideaciones_theme.popup.register', function (require) {
'use strict';

var core = require('web.core');
var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');
var _t = core._t;
var ajax = require('web.ajax');
const dom = require('web.dom');
var qweb = core.qweb;

    //this ajax call is for populate titles data in combobox
    var titles = [];
    ajax.jsonRpc("/get/titles", 'call', {}, {
        'async': false
    }).then(function (data) {
        titles.push(data);
        var opt = "<option value='' selected>Seleccione</option>";
        for(var i=0;i<titles[0].length;i++){
            //console.log(result[0][i].id)
            opt += "<option value='" + titles[0][i].id + "'>" + titles[0][i].shortcut + "</option>";
        }
        $(".sel-title").html(opt);
    });

    //this ajax call is for populate countries data in combobox
    var countries = [];
    ajax.jsonRpc("/get/countries", 'call', {}, {
        'async': false
    }).then(function (data) {
        countries.push(data);
        var opt = "<option value='' selected>Seleccione</option>";
        for(var i=0;i<countries[0].length;i++){
            opt += "<option value='" + countries[0][i].id + "'>" + countries[0][i].name + "</option>";
        }
        $(".sel-country").html(opt);
    });

    //for showing modal with privacy data in pages needed
    $(document).ready(function () {
        //if modal privacy showing it
        $('#oe_privacy_popup_modal').modal('show');
    });

});
