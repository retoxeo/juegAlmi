# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions  # type: ignore

class Skin(models.Model):
    _name = 'skin'
    _description = 'Skin'

    name = fields.Char(string='Name', required=True)
    price = fields.Integer(string='Price', default=0)
    image = fields.Image(string='Image')

