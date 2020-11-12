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
import xlsxwriter
import base64
import io

class StaLibroComprasWizard(models.TransientModel):
    _name = 'sta.reporte_libro_compras_wizard'

    fecha_inicio = fields.Date(string="Fecha inicio")
    fecha_fin = fields.Date(string="Fecha fin")
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')


    @api.multi
    def print_report(self):
        data = {
             'ids': [],
             'model': 'sta.reporte_libro_compras_wizard',
             'form': self.read()[0]
        }
        return self.env.ref('sta.action_report_libro_compras').report_action(self, data=data)


    def reporte_excel(self):
        for w in self:
            dict = {}
            dict['fecha_inicio'] = w['fecha_inicio']
            dict['fecha_fin'] = w['fecha_fin']
            res = self.env['report.sta.reporte_libro_compras'].compras(dict)

            f = io.BytesIO()
            libro = xlwt.Workbook(f)
            hoja = libro.add_sheet('Libro compras')

            estilo_borde = xlwt.easyxf('border: bottom thin, left thin,right thin, top thin')
            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 58, 137, 255)


            hoja.write(0, 0, 'Nombre o Razón social:')
            hoja.write(0, 1, 'Soluciones Tecnologicas de Almacenaie, S.A.')
            hoja.write(1, 0, 'Nombre Comercial:')
            hoja.write(1, 1, 'STA')
            hoja.write(2, 0, 'NIT:')
            hoja.write(2, 1, '9542372-9')

            hoja.write(3,9, 'Folio:')

            hoja.write(4,6,'LIBRO  DE  COMPRAS')
            hoja.write(5,6, 'Del ' + str(w['fecha_inicio']) + ' al ' + str(w['fecha_fin']))
            hoja.write(6,6, 'En Quetzales')

            hoja.write(8,0, 'Fecha Documento',estilo_borde)
            hoja.write(8,1, 'Serie',estilo_borde)
            hoja.write(8,2, 'No Documento',estilo_borde)
            hoja.write(8,3, 'Clase Documento',estilo_borde)
            hoja.write(8,4, 'NIT o Cédula',estilo_borde)
            hoja.write(8,5, 'Nombre del Proveedor',estilo_borde)
            hoja.write(8,6, 'Valor de importaciones',estilo_borde)
            hoja.write(8,7, 'Valor de servicios recibidos',estilo_borde)
            hoja.write(8,8, 'Precio de los bienes')
            hoja.write(8,9, 'Valor IVA',estilo_borde)
            hoja.write(8,10, 'Total',estilo_borde)
            hoja.write(8,11, '',estilo_borde)
            hoja.write(8,12, 'Concepto',estilo_borde)
            linea = 9
            for factura in res:
                hoja.write(linea,0,factura['fecha'])
                hoja.write(linea,1,factura['serie'])
                hoja.write(linea,2,factura['dte_factura'])
                hoja.write(linea,3,factura['clase'])
                hoja.write(linea,4,factura['nit'])
                hoja.write(linea,5,factura['nombre'])
                hoja.write(linea,6,factura['valor_importacion'])
                hoja.write(linea,7,factura['servicio'])
                hoja.write(linea,8,factura['bien'])
                hoja.write(linea,9,factura['iva'])
                hoja.write(linea,10,factura['total'])
                hoja.write(linea,11,factura['transaccion'])
                hoja.write(linea,12,factura['concepto'])
                hoja.write(linea,13,factura['p_g'])
                hoja.write(linea,14,factura['precio_galon'])
                hoja.write(linea,15,factura['sin_iva_gasolina'])
                hoja.write(linea,16,'sin iva')
                linea += 1

            f = io.BytesIO()
            libro.save(f)
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo':datos, 'name':'reporte_libro_compras.xls'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sta.reporte_libro_compras_wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
