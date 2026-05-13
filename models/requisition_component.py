# -*- coding: utf-8 -*-
"""Requisition Component Model"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RequisitionComponent(models.Model):
    """Requisition Component Model"""
    _name = 'requisition.component'
    _description = 'Requisition Component'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  default=lambda self: self.env.user.employee_id,
                                  readonly=True)
    line_ids = fields.One2many('requisition.line',
                               'requisition_id',
                               string='Lines',
                               ondelete='cascade')
    create_po = fields.Boolean(default=False)
    create_internal_transfer = fields.Boolean(default=False)
    po_count = fields.Integer(compute='_compute_counts', store=True)
    internal_count = fields.Integer(compute='_compute_counts', store=True)
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Orders')
    internal_transfer_ids = fields.Many2many('stock.picking', string='Internal Transfers')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('manager', 'Manager Approved'),
        ('head', 'Head Approved'),
        ('rejected', 'Rejected'),
    ], default='draft')

    @api.depends('purchase_order_ids', 'internal_transfer_ids')
    def _compute_counts(self):
        for record in self:
            record.po_count = len(record.purchase_order_ids)
            record.internal_count = len(record.internal_transfer_ids)

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
        """Manager approval button action"""
        self.state = 'manager'

    def action_head(self):
        """Head approval button action"""
        self.state = 'head'

    def action_create_po(self):
        """"Create PO action for opening the wizard"""
        if self.state != 'head':
            raise ValidationError('PO can create only after the approval of the head')
        return {
            'name': 'Create PO',
            'type': 'ir.actions.act_window',
            'res_model': 'create.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_line_ids': self.line_ids.ids, 'default_create_type': 'po',
                        'default_parent_id': self.id},
        }

    def action_create_in(self):
        """Create Internal Transfer action for opening the wizard"""
        if self.state != 'head':
            raise ValidationError('PO can create only after the approval of the head')
        return {
            'name': 'Create Internal Transfer',
            'type': 'ir.actions.act_window',
            'res_model': 'create.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_line_ids': self.line_ids.ids, 'default_create_type': 'in',
                        'default_parent_id': self.id}
        }

    def action_reject(self):
        """Reject button action"""
        self.state = 'rejected'

    def action_po(self):
        """PO smart button action"""
        return {
            'name': 'Purchase Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
        }

    def action_in(self):
        """Internal Transfer smart button action"""
        return {
            'name': 'Internal Transfers',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.internal_transfer_ids.ids)],
        }


class RequisitionLine(models.Model):
    """Requisition line model"""
    _name = 'requisition.line'
    _description = 'Requisition Line'

    requisition_id = fields.Many2one('requisition.component', string='Requisition')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=0.0, required=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='Units')
    qty_on_hand = fields.Float(string='Qty On Hand', related='product_id.qty_available')
