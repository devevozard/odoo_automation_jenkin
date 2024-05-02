from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class AvailibilityCalendar(models.Model):
    _name = 'avail.calendar'


    name = fields.Char(string="Calendar Name")
    calendar_line_ids = fields.One2many('avail.calendar.line','calendar_id',string="Calendar Line")
    

class AvailibilityCalendarLine(models.Model):
    _name = 'avail.calendar.line'

    calendar_id = fields.Many2one('avail.calendar', string="Calendar")
    technician_id = fields.Many2one('hr.employee',string="Technician")
    working_day = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        
    ],string="Day",default="monday")
    working_from = fields.Float(string="From")
    working_to = fields.Float(string="To")
    total_avail_hours = fields.Float(string="Total Avail. Hours",
        compute='_compute_total_avail_hours' )


    @api.constrains('working_from', 'working_to')
    def _check_valid_time(self):
        for record in self:
            if record.working_from and record.working_to and record.working_from >= record.working_to:
                raise ValidationError('Start time must be earlier than end time.')
    
    @api.depends('working_from','working_to')
    def _compute_total_avail_hours(self):
        for rec in self:
            if rec.working_from and rec.working_to:
                rec.total_avail_hours = (rec.working_to - rec.working_from )
            else:
                rec.total_avail_hours = 0.0

            
    
    
    

    



