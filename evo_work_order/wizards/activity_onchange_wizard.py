from odoo import api, fields, models


class ActivityOnchangeWizard(models.TransientModel):
    _name = 'activity.onchange.wizard'

    old_activity_type_id = fields.Many2one('activity.type', string='Old Activity Type')
    category_id = fields.Many2one('product.category', string="Product Category")
    new_activity_type_id = fields.Many2one('activity.type', string='New Activity Type')

    def action_create_new_workorder(self):
        active_id = self._context.get('active_id')
        work_order = self.env['work.order'].browse(active_id)
        new_work_order = work_order.copy(default={'activity_type': self.new_activity_type_id.id,
                                                  'reference_id': work_order.id,
                                                  'is_reprogrammed' : True,
                                                   })

    def action_create_new_workorder(self):
        active_id = self._context.get('active_id')
        if not active_id:
            return
        work_order = self.env['work.order'].browse(active_id)
        if not work_order:
            return
        if not self.new_activity_type_id:
            return

        new_work_order_vals = {
            'activity_type': self.new_activity_type_id.id,
            'reference_id': work_order.id,
            'is_reprogrammed': True,
        }
        new_work_order = work_order.copy(default=new_work_order_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'work.order',
            'view_mode': 'form',
            'res_id': new_work_order.id,
        }

        
    def action_reschedule(self):
        active_id = self._context.get('active_id')
        if not active_id:
            return
        work_order = self.env['work.order'].browse(active_id)
        if not work_order:
            return
        if work_order and self.new_activity_type_id:
            work_order.with_context(from_wizard=True).activity_type = self.new_activity_type_id
            work_order.onchange_activity_type()
        

    