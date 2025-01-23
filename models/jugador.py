# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions  # type: ignore


class Jugador(models.Model):
    _name = 'jugador'
    _description = 'Jugador'
    #_inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='restrict',
        auto_join=True,
        index=True,
        string='Related Partner',
    )

    nickname = fields.Char(string='Nickname', required=True)
    password = fields.Char(string='Password', required=True)
    coins = fields.Integer(string='Coins', default=150)
    xp = fields.Integer(string='XP', default=0)

    skin_ids = fields.Many2many(
        'skin', 
        string='Skins',
        relation='jugador_skin_rel',
        column1='jugador_id',
        column2='skin_id'
    )
    
    image = fields.Image(string='Image')

    level = fields.Integer(
        string='Level',
        compute='_compute_level',
        store=True
    )

    @api.depends('xp')
    def _compute_level(self):
        for record in self:
            record.level = record.xp // 150

    skin_count = fields.Integer(
        string='Número de Skins', 
        compute='_compute_skin_count', 
        store=True
    )
    
    @api.depends('skin_ids')
    def _compute_skin_count(self):
        for record in self:
            record.skin_count = len(record.skin_ids)

    _sql_constraints = [
        ('partner_id_uniq', 'unique(partner_id)', 'A partner can only be associated with one player.')
    ]

