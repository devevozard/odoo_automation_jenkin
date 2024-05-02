from odoo import api, fields, models


class WorkOrderWizard(models.TransientModel):
    _name = 'workorder.wizard'
    _rec_name = 'stock_warehouse_id'

    name = fields.Char('Name')
    schedule_start_date = fields.Datetime(string="Scheduled Start Date")
    responsible_id = fields.Many2one('hr.employee', string="Responsible")
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    category_id = fields.Many2one('product.category', string="Product Category")
    activity_type_id = fields.Many2one('activity.type', string='Activity Type', domain="[('category_id', '=', category_id)]")
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    def action_create_workorder(self):
        workorder_vals = {
        	'name' : self.name,
            'schedule_start_date': self.schedule_start_date,
            'responsible_id': self.responsible_id.id,
            'stock_warehouse_id': self.stock_warehouse_id.id,
            'category_id': self.category_id.id,
            'activity_type': self.activity_type_id.id,
            'planned_hrs' : self.activity_type_id.estimated_time,
        }
        self.env['work.order'].create(workorder_vals)
        return {
            'type': 'ir.actions.act_window_close',
        }
    	