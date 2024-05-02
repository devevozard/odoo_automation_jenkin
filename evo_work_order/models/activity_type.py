from odoo import api, fields, models

class ActivityType(models.Model):
    _name = 'activity.type'

    name = fields.Char(string="Name")
    estimated_time = fields.Float(string="Estimated Time")
    work_order_id = fields.Many2one('work.order', string="Work Order")
    activity_protocol_ids = fields.Many2many('activity.type.detail', string="Activity Types")
    # activity_protocols_ids = fields.One2many('activity.type.detail', 'activity_type_id', string="Activity Types")
    product_detail_ids = fields.One2many('product.template.line', 'activity_prd_id', string="Product Detail")
    category_id = fields.Many2one('product.category', string="Product Category")

    
class ActivityTypeDetail(models.Model):
    _name = 'activity.type.detail'

    workorder_id = fields.Many2one('work.order', string='Work order')
    activity_type_id = fields.Many2one('activity.type', string="Type ID")
    name = fields.Char(string="Name")
    type = fields.Selection([('boolean','True/False'),('text','Text'),('not_avail','N/A')],string='Type')
    code = fields.Integer("Code")

class ActivityTypeLine(models.Model):
    _name = 'activity.type.line'

    workorder_id = fields.Many2one('work.order', string='Work order')
    activity_types_id = fields.Many2one('activity.type.detail', string="Name")
    # name = fields.Char(string="Name")
    types = fields.Selection([('boolean','True/False'),('text','Text'),('not_avail','N/A')],string='Type')
    file_name = fields.Char(string='File Name')
    related_file = fields.Binary(string="File")
    value = fields.Char(string="Value")



class ProductTemplateLine(models.Model):
    _name = 'product.template.line'

    work_order_id = fields.Many2one('work.order', string='Work order')
    activity_prd_id = fields.Many2one('activity.type',  string='Activity Product ID')
    product_id = fields.Many2one('product.product', string="Product")
    product_qty = fields.Float(string="Quantity")
    product_uom = fields.Many2one('uom.uom', string="Uom")


    