# -*- coding: utf-8 -*-
from odoo import models, fields,api
from odoo.exceptions import ValidationError


class RequisitionComponent(models.Model):
    _name = 'requisition.component'
    _description = 'Requisition Component'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee',default=lambda self: self.env.user.employee_id,readonly=True)
    line_ids = fields.One2many('requisition.line', 'requisition_id', string='Lines')
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
        self.state = 'requested'
    def action_manager(self):
        self.state = 'manager'
    def action_head(self):
        for product in self.line_ids:
            if product.product_id.qty_available < product.quantity:
                self.create_po = True
            else:
                self.create_internal_transfer = True
        self.state = 'head'
    # def action_create_po(self):
    #     self.env['purchase.order'].create({
    #         'partner_id'
    #     })
    def action_reject(self):
        self.state = 'rejected'

class RequisitionLine(models.Model):
    _name = 'requisition.line'
    _description = 'Requisition Line'

    requisition_id = fields.Many2one('requisition.component', string='Requisition')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=0.0)




