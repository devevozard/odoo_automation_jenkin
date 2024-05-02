from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
   
class WorkOrderReportWizard(models.TransientModel):
    _name = 'workorder.report.wizard'
    _rec_name = 'warehouse_id'

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    duraction = fields.Selection([('today', 'Today'), ('week', 'Week'), ('month', 'Month')], string='Duration')

    def action_workorder_report(self):
        today = fields.Date.today()
        existing_reports = self.env['workorder.report'].search([])
        existing_reports.unlink()
        for rec in self:
            if rec.duraction == 'today':
                rec._create_daily_report(today)
            elif rec.duraction == 'week':
                monday_of_current_week = today - timedelta(days=today.weekday())
                for i in range(7):
                    day = monday_of_current_week + timedelta(days=i)
                    rec._create_daily_report(day)
            elif rec.duraction == 'month':
                first_day_of_month = today.replace(day=1)
                next_month = first_day_of_month + relativedelta(months=1)
                last_day_of_month = next_month - timedelta(days=1)
                
                current_date = first_day_of_month
                while current_date <= last_day_of_month:
                    rec._create_daily_report(current_date)
                    current_date += timedelta(days=1)

        action = self.env.ref('evo_work_order.action_workorder_report_kanban').read()[0]
        action['target'] = 'main'
        return action

    def _create_daily_report(self, date):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for rec in self:
            total_hours = 0
            if rec.warehouse_id:
                day_of_week = date.weekday()
                day_name = days[day_of_week]
                for warehouse_line in rec.warehouse_id.warehouse_line_ids:
                    total_hours += getattr(warehouse_line, day_name, 0)
            work_orders = self.env['work.order'].search([
                ('stock_warehouse_id', '=', rec.warehouse_id.id),
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
                'stock_warehouse_id': rec.warehouse_id.id,
                'day_name': day_name,
                'total_workorders':len(order),
                'date': date,
                'percentage': percentage
            })