from odoo import api, fields, models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    calendar_avalibility_id = fields.Many2one('avail.calendar', string="Availability Calendar")
    warehouse_line_ids = fields.One2many('ware.house.line', 'ware_house_id', compute='_compute_warehouse_line_ids', store=True, string="Warehouses")

    @api.depends('calendar_avalibility_id')
    def _compute_warehouse_line_ids(self):
        for record in self:
            
            if record.calendar_avalibility_id:
                calendar_id = record.calendar_avalibility_id

                if calendar_id.calendar_line_ids:
                    unique_technician_ids = set()
                    technician_data = {}

                    for calendar_line in calendar_id.calendar_line_ids:
                        if calendar_line.technician_id and calendar_line.working_day:
                            unique_technician_ids.add(calendar_line.technician_id.id)

                            if calendar_line.technician_id.id not in technician_data:
                                technician_data[calendar_line.technician_id.id] = {
                                    'monday': 0,
                                    'tuesday': 0,
                                    'wednesday': 0,
                                    'thursday': 0,
                                    'friday': 0,
                                    'saturday': 0,
                                    'sunday': 0,
                                }
                            technician_data[calendar_line.technician_id.id][calendar_line.working_day] += calendar_line.total_avail_hours
                    

                    warehouse_lines = []
                    for technician_id, hours_data in technician_data.items():
                        technician = self.env['hr.employee'].browse(technician_id)
                        vals = {
                            'ware_house_id': record.id,
                            'technician_name': technician.id,
                            'monday': hours_data['monday'],
                            'tuesday': hours_data['tuesday'],
                            'wednesday': hours_data['wednesday'],
                            'thursday': hours_data['thursday'],
                            'friday': hours_data['friday'],
                            'saturday': hours_data['saturday'],
                            'sunday': hours_data['sunday'],
                        }
                        warehouse_lines.append((0, 0, vals))
                    calendar_avalibility_id = record.calendar_avalibility_id

                    record.write({'warehouse_line_ids': [(5, 0, 0)]})
                    record.calendar_avalibility_id = calendar_avalibility_id
                    record.write({'warehouse_line_ids': warehouse_lines})


class WareHouseLine(models.Model):
    _name = 'ware.house.line'

    ware_house_id = fields.Many2one('stock.warehouse',string="Warehouse")
    technician_name = fields.Many2one('hr.employee',string="Technician")
    monday = fields.Float(string='Monday')
    tuesday = fields.Float(string="Tuesday")
    wednesday= fields.Float(string='Wednesday')
    thursday = fields.Float(string="Thursday")
    friday = fields.Float(string="Friday")
    saturday = fields.Float(string='Saturday')
    sunday = fields.Float(string="Sunday")

    