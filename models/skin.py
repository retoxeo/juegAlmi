# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions  # type: ignore

class Skin(models.Model):
    _name = 'skin'
    _description = 'Skin'

    name = fields.Char(string='Name', required=True)
    price = fields.Integer(string='Price', default=0)
    image = fields.Image(string='Image')
    
    jugador_ids = fields.Many2many(
        'jugador', 
        string='Players',
        relation='jugador_skin_rel', 
        column1='skin_id',
        column2='jugador_id'
    )
    
    player_count = fields.Integer(
        string='Número de Jugadores',
        compute='_compute_player_count',
        store=True
    )
    
    @api.depends('jugador_ids')
    def _compute_player_count(self):
        for record in self:
            record.player_count = len(record.jugador_ids)