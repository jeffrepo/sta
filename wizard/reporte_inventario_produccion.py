# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning
from openerp.osv.orm import except_orm
import time
import base64
import xlwt
import io
import logging
import requests
import json
from datetime import date
import datetime
import datetime
from datetime import datetime
import glob
import time
import openpyxl


class StaInventarioProduccionWizard(models.TransientModel):
    _name = 'sta.reporte_inventario_produccion_wizard'

    producto_id = fields.Many2one("produc.product", string="Producto")
    ubicacion_id = fields.Many2one("stock.location", string="Ubicacion")

    @api.multi
    def print_report(self):
        data = {
             'ids': [],
             'model': 'sta.reporte_inventario_produccion_wizard',
             'form': self.read()[0]
        }
        return self.env.ref('sta.action_report_inventario_produccion').report_action(self, data=data)
