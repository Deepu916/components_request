# -*- coding: utf-8 -*-
from email.policy import default

from odoo import fields, models, api


class CreatePo(models.TransientModel):
    _name = 'create.po'
    _description = 'Create Po'

    create_type = fields.Selection([
        ('po', 'PO'),
        ('in','IN')
    ],default=lambda self:self.env.context.get('create_type'))
    partner_id = fields.Many2many('res.partner',string='Vendors',required=True)
    line_ids = fields.Many2many('requisition.line',ondelete='cascade',required=True)
    quantity = fields.Float(string='Quantity',required=True)
    creation_type = fields.Char(string='Creation Type',required=True,default=lambda self:self.env.contex.get('creation_type'))
    def action_create_purchase_order(self):
        for ids in self.partner_id:
            order = self.env['purchase.order'].create(
                {
                    'partner_id':ids.id,
                }
            )
            for line in self.line_ids:
                self.env['purchase.order.line'].create({
                    'order_id': order.id,
                    'product_id': line.product_id.id,
                    'product_qty':line.quantity,
                })
    # def action_create_internal_transfer(self):

