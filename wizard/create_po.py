# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CreatePo(models.TransientModel):
    """Create Po Wizard"""
    _name = 'create.po'
    _description = 'Create Po'


    partner_ids = fields.Many2many('res.partner',string='Vendors',required=True)
    line_ids = fields.Many2many('requisition.line',ondelete='cascade',required=True)
    destination_location_id = fields.Many2one('stock.location',string='Destination Location')
    create_type = fields.Char(string='Create Type')
    parent_id = fields.Many2one('requisition.component')
    orders = []
    internal = []


    def action_create_purchase_order(self):
        """Create Purchase Order action"""
        self.parent_id.order_ids.clear()
        for ids in self.partner_ids:
            order = self.env['purchase.order'].create(
                {
                    'partner_id':ids.id,
                }
            )
            self.parent_id.order_ids.append(order.id)
            self.orders.append(order.id)
            for line in self.line_ids:
                if line.qty_on_hand < line.quantity:
                    self.env['purchase.order.line'].create({
                        'order_id': order.id,
                        'product_id': line.product_id.id,
                        'product_qty': line.quantity,
                    })
        self.parent_id.po_count = len(self.orders)
        self.parent_id.create_po = False
        self.parent_id.po_smart = True
        print(len(self.partner_ids))

    def action_create_internal_transfer(self):
        """create internal transfer action"""
        picking_type_id = self.env['stock.picking.type'].search([('name','=','Internal Transfers')])
        print("picking type",picking_type_id)

        for line in self.line_ids:
            if line.qty_on_hand > line.quantity:
                quant = self.env['stock.quant'].search([('product_id','=',line.product_id)],limit=1)
                stock = self.env['stock.picking'].create({
                    'picking_type_id': picking_type_id.id,
                    'partner_id':self.env.user.employee_id.id,
                    'location_id':quant.location_id.id,
                    'location_dest_id':self.destination_location_id.id,
                })
                self.internal.append(stock.id)
                self.parent_id.internal_ids.append(stock.id)
                self.env['stock.move'].create({
                    'picking_id':stock.id,
                    'product_id':line.product_id.id,
                    'product_uom_qty':line.quantity,
                })
        print(len(self.internal))
        self.parent_id.internal_count = len(self.internal)
        self.parent_id.create_internal_transfer = False
        self.parent_id.in_smart = True
        stock.button_validate()
        print(self.parent_id.create_internal_transfer)
