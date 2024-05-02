import datetime
from odoo import api, fields, models, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError


class WorkOrder(models.Model):
    _name = 'work.order'
   
    name = fields.Char(string="Name")
    schedule_start_date = fields.Datetime(string="Scheduled Start Date")
    schedule_end_date = fields.Datetime(string="Scheduled End Date",)
    deadline_date = fields.Date(string="DeadLine")
    planned_hrs = fields.Float(string='Planned hours')
    responsible_id = fields.Many2one('hr.employee', string="Responsible")
    category_id = fields.Many2one('product.category', string="Product Category")
    product_id = fields.Many2one('product.product', string="Product")
    partner_id = fields.Many2one('res.partner', string="Customer")
    contact_city = fields.Char(string='Contact City')
    contact_address = fields.Char(string='Contact Address')
    contact_phone = fields.Char(string='Contact Phone')
    contact_email = fields.Char(string='Contact Email')
    contact_zip = fields.Char(string='Zip')
    contact_state = fields.Many2one('res.country.state', string="Contact State")
    contact_country = fields.Many2one('res.country', string='Contact Country')
    lot_serial = fields.Many2one('stock.production.lot', string="Lot/Serial No.")
    activity_type = fields.Many2one('activity.type', string='Activity Type', domain="[('category_id', '=', category_id)]")
    employee_id = fields.Integer('Employee ID')
    activity_types_ids = fields.One2many('activity.type', 'work_order_id')
    reference_no = fields.Char(string='Wo Number', required=True, readonly=True, default=lambda self: _('New'))
    # activity_protocol_ids = fields.Many2many('activity.type.detail', string="Activity Types")
    activity_protocols_ids = fields.One2many('activity.type.line', 'workorder_id', string="Activity Types")
    product_details_ids = fields.One2many('product.template.line', 'work_order_id',  string="Product Detail")
    timesheet_ids = fields.One2many('timesheet.line', 'wo_order_id', string="Timesheet")
    total_hours = fields.Float("Hours Spent", compute='_compute_total_hours', compute_sudo=True)
    breaking_interval_ids = fields.One2many('break.tracking','workorder_id', string="Breaking Time")
    total_breaking_hours = fields.Float("Total Breaking Hours", compute='_compute_total_breaking_hours', compute_sudo=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('schedule', 'Schedule'), ('inprogress', 'In Progress'),('done', 'Done')], default='draft',string='WorkOrder Status')
    images = fields.Binary(string="Images")
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    calculate_percentage = fields.Float('Work Load Percentage')
    image_ids = fields.One2many('ir.attachment', 'work_order_id', string=" Images", compute='_compute_get_image')
    reference_id = fields.Many2one('work.order', string='Origin')
    is_reprogrammed = fields.Boolean(string='Reprogrammed', default=False)
    timer_flag = fields.Boolean(string='Timer Flag', default=False)
    state_flag_smith = fields.Selection([('start', 'Start'),
                              ('pause', 'Pause'),
                              ('restart', 'Restart'),
                              ('done', 'Done')], default='start')
    responsible_availability_ids = fields.One2many('responsible.availability', 'work_order_id', string='Responsible Avail',
                                compute='_compute_responsible_availability')

    def _compute_responsible_availability(self):
        responsible_availability = self.env['responsible.availability'].search([])
        for rec in self:
            if responsible_availability:
                rec.responsible_availability_ids = responsible_availability
            else:
                rec.responsible_availability_ids

    @api.model
    def button_start(self, idd=-1):
        if idd != -1:
            rec = self.browse(idd)
            if rec:
                rec.state_flag_smith = 'pause'
                return True

    @api.model
    def button_pause(self, idd=-1):
        if idd != -1:
            rec = self.browse(idd)
            if rec:
                rec.state_flag_smith = 'restart'
                return True

    @api.model
    def button_restart(self, idd=-1):
        if idd != -1:
            rec = self.browse(idd)
            if rec:
                rec.state_flag_smith = 'pause'
                return True

    @api.model
    def button_done(self, idd=-1):
        if idd != -1:
            rec = self.browse(idd)
            if rec:
                rec.state_flag_smith = 'start'
                return True

    def _compute_get_image(self):
        for rec in self:
            images = self.env['ir.attachment'].sudo().search([('res_model', '=', 'work.order'),
                                                  ('res_id', '=', rec.id)])
            if images:
                rec.image_ids = images
            else:
                rec.image_ids = False

    @api.onchange('timesheet_ids')
    def _onchange_timesheet_ids(self):
        for rec in self:
            if any(timesheet.start_time for timesheet in rec.timesheet_ids):
                rec.state = 'inprogress'
                break
    
    @api.onchange('schedule_start_date','planned_hrs')
    def _onchange_end_date(self):
        for record in self:
            if record.schedule_start_date and record.planned_hrs:
                record.schedule_end_date = record.schedule_start_date + timedelta(hours=record.planned_hrs)

    
    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'work.order') or _('New')
        res = super(WorkOrder, self).create(vals)
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        default['reference_no'] = self.env['ir.sequence'].next_by_code('work.order')
        return super(WorkOrder, self).copy(default)

    @api.onchange('responsible_id')
    def onchange_responsible(self):
        if self.responsible_id:
            self.employee_id = self.responsible_id.id

    def check_timesheet(self, idd=-1):
        if idd != -1:
            rec = self.browse(idd)
            if not rec.timesheet_ids:
                return False
            else:
                for item in rec.timesheet_ids:
                    if not item.end_time:
                        rec.timer_flag = True
                        break
                return True

    @api.onchange('category_id')
    def _onchange_category_id(self):
        for rec in self:
            if rec.category_id != rec.activity_type.category_id:
                rec.activity_type = False

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            partner_id = self.env['res.partner'].sudo().search([('id', '=', self.partner_id.id)])
            self.contact_email = partner_id.email
            self.contact_address = partner_id.street
            self.contact_city = partner_id.city
            self.contact_state = partner_id.state_id
            self.contact_country = partner_id.country_id
            self.contact_zip = partner_id.zip
            self.contact_phone = partner_id.phone

    # @api.depends('activity_type')
    # def _compute_product_details(self):
    #     for order in self:
    #         if order.activity_type:
    #             order.product_details_ids = order.activity_type.product_detail_ids
    #             order.planned_hrs = order.activity_type.estimated_time
    #         else:
    #             order.product_details_ids = [(5, 0, 0)]

    
    @api.onchange('activity_type')
    def onchange_activity_type(self):
        if self.activity_type:
            self.planned_hrs = self.activity_type.estimated_time
            self.activity_protocols_ids = [(5, 0, 0)]
            self.product_details_ids = [(5, 0, 0)]
            activity_protocol_type_ids = self.env['activity.type'].sudo().search([('id', '=', self.activity_type.id)])
            for activity_protocol_type_id in activity_protocol_type_ids:
                if activity_protocol_type_id.activity_protocol_ids:
                    for protocol_id in activity_protocol_type_id.activity_protocol_ids:
                        self.activity_protocols_ids = [(0, 0, {
                            'activity_types_id': protocol_id.id,
                            'types': protocol_id.type
                        })]

                if activity_protocol_type_ids.product_detail_ids:
                    for product in activity_protocol_type_ids.product_detail_ids:
                        self.product_details_ids = [(0,0,{
                            'product_id':product.product_id.id,
                            'product_qty':product.product_qty,
                            'product_uom':product.product_uom.id,

                        })]
                        
    def change_activity(self):
        action = self.env.ref('evo_work_order.action_activity_onchange_wizard').read()[0]
        action['context'] = {'default_old_activity_type_id': self.activity_type.id,
                             'default_category_id' : self.category_id.id}
        return action
    
    @api.depends('timesheet_ids.duration')
    def _compute_total_hours(self):
        for rec in self:
            total_hours = 0.0
            if rec.timesheet_ids:
                total_hours = sum(rec.timesheet_ids.mapped('duration'))
            rec.update({"total_hours": total_hours})

    @api.depends('breaking_interval_ids.total_duration')
    def _compute_total_breaking_hours(self):
        for rec in self:
            total_hours = 0.0
            if rec.breaking_interval_ids:
                total_hours = sum(rec.breaking_interval_ids.mapped('total_duration'))
            rec.update({"total_breaking_hours": total_hours})


    @api.onchange('schedule_start_date', 'planned_hrs','stock_warehouse_id')
    def _compute_percentage(self):
        self.calculate_percentage = False
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for rec in self:
            if rec.schedule_start_date:
                day_of_week = rec.schedule_start_date.weekday()
                day_name = days[day_of_week]
                total_hours = 0
                if day_name and rec.stock_warehouse_id:
                    for warehouse_line in rec.stock_warehouse_id.warehouse_line_ids:
                        total_hours += getattr(warehouse_line, day_name, 0)

                schedule_date = rec.schedule_start_date.date()
                work_orders = self.env['work.order'].search([
                    ('stock_warehouse_id', '=', rec.stock_warehouse_id.id),
                ])
                order = []
                for work in work_orders:
                    if work.schedule_start_date:
                        if work.schedule_start_date.date() == schedule_date:
                           order.append(work)
                workorder_planned_hours =rec.planned_hrs + sum(workorder.planned_hrs for workorder in order)
                if total_hours > 0:
                    percentage = (workorder_planned_hours / total_hours) * 100
                    self.calculate_percentage = percentage

    def write(self, values):
        if 'activity_type' in values and self.activity_type:
            if not self._context.get('from_wizard'):
                raise ValidationError("You need change the activity from the 'Change Activity' button.")
        return super(WorkOrder, self).write(values)

    def view_responsible_availability(self):
        existing_records = self.env['responsible.availability'].search([])
        existing_records.unlink()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if self.schedule_start_date:
            date = self.schedule_start_date.date()
            day_name = days[date.weekday()]
            calendar = self.env['avail.calendar'].search([])
            technicians = calendar.mapped('calendar_line_ids.technician_id')
            technician_hours = {}
            for technician in technicians:
                lines = calendar.calendar_line_ids.filtered(lambda line: line.technician_id == technician and line.working_day == day_name)
                total_hours = sum(line.total_avail_hours for line in lines)
                work_orders = self.env['work.order'].search([
                    ('responsible_id', '=', technician.id),
                ])
                order = []
                for work in work_orders:
                    if work.schedule_start_date:
                        if work.schedule_start_date.date() == date:
                           order.append(work)
                workorder_planned_hours = sum(workorder.planned_hrs for workorder in order)
                if total_hours > 0:
                    percentage = (workorder_planned_hours / total_hours) * 100
                else:
                    percentage = 0.0
        
                self.env['responsible.availability'].create({
                    'date':self.schedule_start_date.date(),
                    'responsible_id': technician.id,
                    'percentage': percentage
                })


class TimesheetLines(models.Model):
    _name = 'timesheet.line'

    employee_id = fields.Many2one('hr.employee',  string='Employee')
    wo_order_id = fields.Many2one('work.order', string='Work order')
    name = fields.Char(string="Description")
    start_time = fields.Datetime(string="Start time")
    end_time = fields.Datetime(string="End time")
    duration = fields.Float(string="Duration", compute='_compute_duration', store=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                start_time = fields.Datetime.from_string(record.start_time)
                end_time = fields.Datetime.from_string(record.end_time)
                duration_cal = (end_time - start_time).total_seconds() / 3600
                record.duration = duration_cal
            else:
                record.duration = 0.0

class BreakTracking(models.Model):
    _name = 'break.tracking'

    hr_employee_id = fields.Many2one('hr.employee',  string='Employee')
    workorder_id = fields.Many2one('work.order', string='Work Order')
    name = fields.Char(string="Description")
    starting_time = fields.Datetime(string="Break Start time")
    ending_time = fields.Datetime(string=" Break End time")
    total_duration = fields.Float(string="Total Duration", compute='_compute_total_duration', store=True)

    @api.depends('starting_time', 'ending_time')
    def _compute_total_duration(self):
        for record in self:
            if record.starting_time and record.ending_time:
                breaking_start_time = fields.Datetime.from_string(record.starting_time)
                breaking_end_time = fields.Datetime.from_string(record.ending_time)
                duration_cal = (breaking_end_time - breaking_start_time).total_seconds() / 3600
                record.total_duration = duration_cal
            else:
                record.total_duration = 0.0

                
class IrAttachment(models.Model):
    _inherit = 'ir.attachment'


    work_order_id = fields.Many2one('work.order', string='Work Order')
                        
                            
                           


