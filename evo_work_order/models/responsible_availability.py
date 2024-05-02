from odoo import api, fields, models

class ResponsibleAvailability(models.Model):
    _name = 'responsible.availability'


    responsible_id = fields.Many2one('hr.employee', string="Responsible")
    date = fields.Date(string='Date')
    percentage = fields.Float(string=' ')
    work_order_id = fields.Many2one('work.order', string='Work Order')