import calendar
from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class WorkorderReport(models.Model):
    _name = 'workorder.report'

    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    date = fields.Date('Date')
    percentage = fields.Float(string=' ')
    day_name = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ], string="Day", default="monday")
    formatted_date = fields.Char(string='Formatted Date', compute='_compute_formatted_date')
    total_workorders = fields.Integer(string="Total WorkOrders")

    @api.depends('date')
    def _compute_formatted_date(self):
        for record in self:
            if record.date:
                day_of_week = record.date.weekday()
                abbreviated_day_name = record.date.strftime('%a')
                formatted_date = record.date.strftime('%Y %b %d')
                record.formatted_date = f"{formatted_date} {abbreviated_day_name} "

    def action_assign(self):
        action = self.env.ref('evo_work_order.action_workorder_wizard').read()[0]
        action['context'] = {
        'default_stock_warehouse_id': self.stock_warehouse_id.id,
        'default_schedule_start_date': self.date,
        }
        return action

    def action_update(self):
        existing_reports = self.env['workorder.report'].search([])
        work_report_length = len(existing_reports)
        warehouse_ids = []
        for report in existing_reports:
            if report.stock_warehouse_id and report.stock_warehouse_id.id not in warehouse_ids:
                warehouse_ids.append(report.stock_warehouse_id.id)
        existing_reports.unlink()
        today = fields.Date.today()
        if work_report_length == 1:
            self._create_daily_report(today, warehouse_ids)
        elif work_report_length == 7:
            monday_of_current_week = today - timedelta(days=today.weekday())
            for i in range(7):
                day = monday_of_current_week + timedelta(days=i)
                self._create_daily_report(day, warehouse_ids)
        elif work_report_length > 7:
                first_day_of_month = today.replace(day=1)
                next_month = first_day_of_month + relativedelta(months=1)
                last_day_of_month = next_month - timedelta(days=1)
                
                current_date = first_day_of_month
                while current_date <= last_day_of_month:
                    self._create_daily_report(current_date,warehouse_ids)
                    current_date += timedelta(days=1)

    
    def _create_daily_report(self, date, warehouse_ids):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for record in self:
            for warehouse_id in warehouse_ids:
                total_hours = 0
                warehouse = self.env['stock.warehouse'].browse(warehouse_id)
                if warehouse:
                    day_of_week = date.weekday()
                    day_name = days[day_of_week]
                    for warehouse_line in warehouse.warehouse_line_ids:
                        total_hours += getattr(warehouse_line, day_name, 0)
                work_orders = self.env['work.order'].search([
                    ('stock_warehouse_id', '=', warehouse_id),
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
                self.env['workorder.report'].create({
                        'stock_warehouse_id': warehouse_id,
                        'day_name': day_name,
                        'total_workorders':len(order),
                        'date': date,
                        'percentage': percentage
                    })