# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HouseProperty(models.Model):
    _name = "house.property"
    _description = "House Property"
    """Building or house intended for housing or another purpose and owned by someone."""

    name = fields.Char(
        string='Name',
        required=True)
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Payment Term',
        required=False)
    rental_type_id = fields.Many2one(
        comodel_name='house.rental.type',
        string='Rental Type',
        required=False)
    property_type_id = fields.Many2one(
        comodel_name='house.property.type',
        string='Property type',
        required=True)
    parent_property = fields.Many2one(
        comodel_name='house.property',
        string='Belongs to Property',
        required=False)
    client_id = fields.Many2one(
        comodel_name='res.partner',
        string='Tenant/Owner',
        required=False)
    description = fields.Text(
        string="Description",
        required=False)
    picture = fields.Binary(string="")
    house_manager_id = fields.Many2one(
        comodel_name='res.partner',
        string='House Manager',
        required=False)
    price_monthly = fields.Float(
        string='Monthly price',
        required=False)
    price_daily = fields.Float(
        string='Daily Price',
        required=False)
    price = fields.Float(
        string='Regular Price',
        required=True)
    location = fields.text(string='Location')
    state = fields.Selection(
        string='State',
        selection=[
            ('free', 'free'),
            ('busy', 'busy'),
            ('reserved', 'reserved'),
        ],
        required=False, )
    location_line_ids = fields.One2many(
        comodel_name='house.location.inside.lines',
        inverse_name='property_id',
        string='Structures',
        required=False)
    amenity_ids = fields.Many2many(
        comodel_name='house.amenities',
        string='Amenities')
    income_account = fields.Many2one(
        comodel_name='account.journal',
        string='Income Account',
        required=False)
    expense_account = fields.Many2one(
        comodel_name='account.journal',
        string='Expense Account',
        required=False)


# Rent, Reservation
class RentalType(models.Model):
    _name = 'house.rental.type'
    _description = 'Rental Type'

    name = fields.Char()
    description = fields.Text()


# Building, House, Room, Floor
class PropertyType(models.Model):
    _name = 'house.property.type'
    _description = 'Property type'

    name = fields.Char()
    description = fields.Text()


class Amenities(models.Model):
    _name = 'house.amenities'
    _description = 'Amenities'

    name = fields.Char()


class LocationHouse(models.Model):
    _name = 'house.location.inside'
    _description = 'Locations inside house'

    name = fields.Char()


class LocationLinesHouse(models.Model):
    _name = 'house.location.inside.lines'
    _description = 'Location Lines for a House'

    name = fields.Many2one(
        comodel_name='house.location.inside',
        string='Name',
        required=False)
    qty = fields.Integer(
        string='Quantity',
        required=False)
    state = fields.Selection(
        string='State',
        selection=[
            ('excellent', 'excellent'),
            ('good', 'good'),
            ('regular', 'regular'),
            ('bad', 'bad'),
        ],
        required=False, )
    property_id = fields.Many2one(
        comodel_name='house.property',
        string='',
        required=False)
