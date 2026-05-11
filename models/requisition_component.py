# -*- coding: utf-8 -*-
from odoo import models, fields,api
from odoo.exceptions import ValidationError


class RequisitionComponent(models.Model):
    _name = 'requisition.component'
    _description = 'Requisition Component'
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee', string='Employee',default=lambda self: self.env.user.employee_id,readonly=True)
    line_ids = fields.One2many('requisition.line', 'requisition_id', string='Lines',ondelete='cascade')
    create_po = fields.Boolean(default=False)
    create_internal_transfer = fields.Boolean(default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('manager', 'Manager Approved'),
        ('head','Head Approved'),
        ('rejected','Rejected'),
    ],default='draft')

    def action_request(self):
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
        self.state = 'manager'
    def action_head(self):
        self.state = 'head'
    def action_create_po(self):
        if self.state!='head':
            raise ValidationError('PO can create only after the approval of the head')
        return{
            'name':'Create PO',
            'type':'ir.actions.act_window',
            'res_model': 'create.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_line_ids': self.line_ids.ids},
        }
    # def action_create_in(self):
    #     return {
    #         'name':'Create Internal Transfer',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'create.po',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'create_type':'internal'}
    #     }
    def action_reject(self):
        self.state = 'rejected'

class RequisitionLine(models.Model):
    _name = 'requisition.line'
    _description = 'Requisition Line'

    requisition_id = fields.Many2one('requisition.component', string='Requisition')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=0.0)
