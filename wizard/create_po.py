# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CreatePo(models.TransientModel):
    _name = 'create.po'
    _description = 'Create Po'


    partner_id = fields.Many2many('res.partner',string='Vendors')
    order_line_ids = fields.One2many('')