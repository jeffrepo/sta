# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
import logging

class Task(models.Model):
    _inherit = "project.task"


    @api.onchange('timesheet_ids')
    def change_lineas_timesheet(self):
        for tarea in self:
            cantidad_empleados = 0
            if tarea.project_id.sale_order_id and tarea.timesheet_ids:
                for linea in tarea.timesheet_ids:
                    cantidad_empleados += 1

                if tarea.project_id.sale_order_id.order_line:
                    logging.warn('timesheet')
                    for linea in tarea.project_id.sale_order_id.order_line:
                        if linea.product_id.product_tmpl_id.empleados:
                            if cantidad_empleados > linea.product_uom_qty and self.env.user.id not in [2,6]:
                                raise UserError(_('Límite de presupuesto, favor pedir autorización'))

                            elif cantidad_empleados > linea.product_uom_qty and self.env.user.id in [2,6]:
                                return
