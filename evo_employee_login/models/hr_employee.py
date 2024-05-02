from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class ResSettings(models.Model):
    _inherit = 'hr.employee'


    pin = fields.Char(string='PIN No')
    cover_pin_no = fields.Char(string="PIN",default="****")
    show_all_wo = fields.Char(string='Show all WOs', default=False)

    _sql_constraints = [
        ('unique_identification_id', 'unique(identification_id)', 'Identification ID must be unique!'),

    ]

    @api.constrains('identification_id')
    def _check_identification_id_unique(self):
        for employee in self:
            if employee.identification_id:
                duplicate_employees = self.search(
                    [('identification_id', '=', employee.identification_id), ('id', '!=', employee.id)])
                if duplicate_employees:
                    raise ValidationError('Identification ID must be unique!')
    
    @api.model
    def custom_login(self, emp_code='', pin=None):
        
        if emp_code and pin is not None:
            domain = [('identification_id','=',emp_code)]
            employee = self.env['hr.employee'].search(domain,  limit=1)

            if employee  and pin == employee.pin :
                return employee.id
            else:
                raise UserError('Invalid employee ID or pin')

        raise UserError('Employee ID and pin are required')  


    def action_reset_to_default_pin(self):
        if self.pin:
            self.write ({'pin':'0000'}) 
            
        


            

