# -*- coding: utf-8 -*-
from odoo import models, fields,api
from odoo.exceptions import ValidationError


class RequisitionComponent(models.Model):
    """Requisition Component class"""
    _name = 'requisition.component'
    _description = 'Requisition Component'
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee', string='Employee',default=lambda self: self.env.user.employee_id,readonly=True)
    line_ids = fields.One2many('requisition.line', 'requisition_id', string='Lines',ondelete='cascade')
    create_po = fields.Boolean(default=False)
    create_internal_transfer = fields.Boolean(default=False)
    po_count = fields.Integer(default=0)
    po_smart = fields.Boolean(default=False)
    in_smart = fields.Boolean(default=False)
    internal_count = fields.Integer(default=0)
    order_ids = []
    internal_ids = []
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('manager', 'Manager Approved'),
        ('head','Head Approved'),
        ('rejected','Rejected'),
    ],default='draft')
    def action_request(self):
        """Request button action"""
        if not self.line_ids:
            raise ValidationError('Product line is empty')
        for product in self.line_ids:
            if not product.quantity:
                raise ValidationError('Quantity is empty')
            if product.product_id.qty_available < product.quantity:
                self.create_po = True
            else:
                self.create_internal_transfer = True
        self.state = 'requested'
    def action_manager(self):
        """Manager approval action"""
        self.state = 'manager'
    def action_head(self):
        """Head approval action"""
        self.state = 'head'
    def action_create_po(self):
        """"Create PO action"""
        if self.state!='head':
            raise ValidationError('PO can create only after the approval of the head')
        return{
            'name':'Create PO',
            'type':'ir.actions.act_window',
            'res_model': 'create.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_line_ids': self.line_ids.ids,'default_create_type':'po','default_parent_id': self.id},
        }
    def action_create_in(self):
        """Create Internal Transfer action"""
        if self.state!='head':
            raise ValidationError('PO can create only after the approval of the head')
        return {
            'name':'Create Internal Transfer',
            'type': 'ir.actions.act_window',
            'res_model': 'create.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_line_ids': self.line_ids.ids,'default_create_type':'in'}
        }
    def action_reject(self):
        """Reject action"""
        self.state = 'rejected'
    # def action_po(self):
    #     """PO smart button action"""
    #     print(self.order_ids)
    #     return{
    #         'name':'Purchase Orders',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'purchase.order',
    #         'view_mode': 'list,form',
    #         'domain':[('id', 'in', self.order_ids)],
    #     }
    # def action_in(self):
    #     """Internal Transfer smart button action"""
    #     return{
    #         'name':'Internal Transfers',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'stock.picking',
    #         'view_mode': 'list,form',
    #         'domain':[('id', 'in', self.internal_ids),('')],
    #     }
class RequisitionLine(models.Model):
    """Requisition line model"""
    _name = 'requisition.line'
    _description = 'Requisition Line'

    requisition_id = fields.Many2one('requisition.component', string='Requisition')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=0.0,required=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='Units')
    po = fields.Boolean(default=False)
    internal = fields.Boolean(default=False)
    qty_on_hand = fields.Float(string='Qty On Hand',related = 'product_id.qty_available')
    source_id = fields.Many2one('stock.location',related='product_id.location_id',string='Source')
    destination_id = fields.Many2one('stock.location', string='Destination Location')
