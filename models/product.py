# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    agrupar_gastos = fields.Boolean('Agrupar gastos en SO')
