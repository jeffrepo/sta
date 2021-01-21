# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import datetime
import logging

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    tipo_factura = fields.Selection([('compra', 'Compra/Bien'), ('servicio', 'Servicio'), ('importacion', 'Importación/Exportación'), ('combustible', 'Combustible'), ('mixto', 'Mixto')], string="Tipo de factura", default="compra")
    serie_factura = fields.Char('Serie factura')
    dte_factura = fields.Char('DTE Factura')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    lote = fields.Char(string="Lote")
    concepto = fields.Char(string="Concepto")

class AccountTax(models.Model):
    _inherit = "account.tax"

    prorrateo = fields.Boolean('Prorrateo')

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    horas_extras = fields.Float('Horas extras')
