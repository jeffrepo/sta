# -*- encoding: utf-8 -*-

from odoo import api, models, fields
import datetime
import time
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime
import logging

class LibroCompras(models.AbstractModel):
    _name = 'report.sta.reporte_libro_compras'

    def compras(self,data):
        datos = []
        fecha_inicio = datetime.datetime.strptime(str(data['fecha_inicio']), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin = datetime.datetime.strptime(str(data['fecha_fin']), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        facturas_compras = self.env['account.invoice'].search([('create_date','>=',fecha_inicio),('create_date','<=',fecha_fin),('state','in',['paid','open'])])
        if facturas_compras:
            for factura in facturas_compras:
                bien = ''
                servicio = ''
                transaccion = ''
                concepto = ''
                propina = 0
                gasolina = 0
                p_g = ''
                precio_galon = 0
                total_galon_sin_iva = 0
                if factura.tipo_factura == 'compra':
                    bien = factura.amount_untaxed
                if factura.tipo_factura == 'servicio':
                    servicio = factura.amount_untaxed
                if factura.payment_ids:
                    for p in factura.payment_ids:
                        transaccion = p.lote
                        concepto = p.communication
                for linea in factura.invoice_line_ids:
                    logging.warn(linea)
                    if 'Propina' in str(linea.product_id.name):
                        propina = linea.price_subtotal
                    if 'Gasolina' in str(linea.product_id.name):
                        gasolina = linea.price_total
                        precio_galon = linea.price_unit
                        total_galon_sin_iva = linea.price_subtotal
                if propina > 0:
                    p_g = propina
                if gasolina > 0:
                    p_g = gasolina
                f = {
                    'fecha': str(factura.date_invoice),
                    'serie': factura.serie_factura,
                    'dte_factura': factura.dte_factura,
                    'clase': 'Factura',
                    'nit': factura.partner_id.vat,
                    'nombre': factura.partner_id.name,
                    'valor_importacion': 0,
                    'servicio': servicio,
                    'bien': bien,
                    'iva': factura.amount_tax,
                    'total': factura.amount_total,
                    'transaccion': transaccion,
                    'concepto': concepto,
                    'p_g': p_g,
                    'precio_galon': precio_galon if precio_galon > 0 else '',
                    'sin_iva_gasolina': total_galon_sin_iva if total_galon_sin_iva else ''
                }
                datos.append(f)
        return datos

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        # diario = selfactura.env['account.move.line'].browse(data['form']['cuentas_id'][0])

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'compras': self.compras,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
