# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
import odoo.addons.decimal_precision as dp
import logging
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    tipo_compra = fields.Selection([('antencion', 'Atencion cliente'),('gastos','Gastos de venta')], string="Tipo")
    cliente_id = fields.Many2one('res.partner','Cliente')
    descuento_global = fields.Float('% Descuento global')
    proyecto_id = fields.Many2one('project.project','Poyecto')
    bloqueado = fields.Boolean('Bloqueado')

    def calcular_descuento(self):
        if self.descuento_global > 0:
            for linea in self.order_line:
                linea.precio_original = linea.price_unit
                linea.discount = self.descuento_global
                # linea.price_unit = linea.price_unit * (1 - linea.discount / 100)
        else:
            for linea in self.order_line:
                linea.precio_original = linea.price_unit
                linea.price_unit = linea.price_unit * (1 - linea.discount / 100)

        return True

    def buscar_producto_compras_proyecto(self,proyecto_id ,producto_id,compra_id):
        valor = 0
        # compra_ids = self.env['purchase.order'].search([('proyecto_id','=',proyecto_id.id),('id','!=',compra_id.id)])
        compra_ids = self.env['purchase.order'].search([('proyecto_id','=',proyecto_id.id)])
        if compra_ids:
            for compra in compra_ids:
                if compra.order_line:
                    for linea in compra.order_line:
                        if linea.product_id.id == producto_id.id:
                            valor += linea.price_total

        return valor

    @api.onchange('order_line')
    def change_lineas_compra(self):
        for compra in self:
            if compra.proyecto_id and compra.proyecto_id.sale_order_id and compra.order_line:
                for linea in compra.order_line:
                    for linea_venta in compra.proyecto_id.sale_order_id.sale_order_option_ids:
                        if linea.product_id.id == linea_venta.product_id.id:
                            logging.warn('si')
                            valor = self.buscar_producto_compras_proyecto(compra.proyecto_id,linea.product_id,compra)
                            if (linea.price_total + valor) > linea_venta.costo and self.env.user.id not in [2,6]:
                                logging.warn('if')
                                raise UserError(_('Límite de presupuesto, favor pedir autorización'))
                            elif (linea.price_total + valor) > linea_venta.costo and self.env.user.id in [2,6]:
                                logging.warn(self.env.user.id)
                                logging.warn('else')
                                return



    # descuento_unitario = fields.Float('Desc. Uni')

    # @api.onchange('precio_original')
    # def onchange_discount(self):
    #     logging.warn('ejejejjee')
    #     self._get_discounted_price_unit()

class PurchaseProrrateo(models.Model):
    _name = "purchase.prorrateo"

    # def default_impuestos(self):
    #     gs = self.env['account.tax'].search([('prorrateo','=',True)])
    #     return [(0, 0, {'impuesto_id': i.id, 'valor_quetzal': 0,'valor_dolar':0}) for i in gs]

    name = fields.Char('Nombre')
    fecha = fields.Date('Fecha')
    tipo_cambio = fields.Float('Tipo de cambio',digits = (12,4))
    compra_ids = fields.Many2many('purchase.order','sta_prorrateo_compra_rel',string="Pedidos de compra")
    compra_prorrateo_linea = fields.One2many('purchase.prorrateo_line','prorrateo_id', string="linea prorrateo")
    prorrateo_impuesto = fields.One2many('purchase.prorrateo_impuesto', 'prorrateo_id', 'Prorrateo impuesto',copy=True)
    euros_a_dolar = fields.Float('Euros a dolar')
    total_gastos_quetzales = fields.Float('Total gastos Q.')
    total_gastos_dolares = fields.Float('Total gastos $.')
    iva = fields.Float('IVA')
    total_por_item = fields.Float('Total por item')
    state = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('gastos', 'Gastos generados'),
        ('prorrateado', 'Prorrateado'),
        ('costo','Costo asignado')
        ], string='Estado', readonly=True, copy=False, index=True, track_visibility='onchange', default='nuevo')

    def asignar_impuesto(self):
        if self.compra_prorrateo_linea:
            costo_dic = {}
            precio_costo = self.env['product.price.history'].create(costo_dic)
        return True

    # @api.onchange('prorrateo_impuesto')
    # def change_lineas_impuestos(self):
    #     total_quetzal = 0
    #     total_dolar = 0
    #     for linea in self.prorrateo_impuesto:
    #         total_quetzal += round(linea.valor_quetzal,4)
    #         total_dolar += round(linea.valor_dolar,4)
    #
    #     logging.warn(total_quetzal)
    #     logging.warn(total_dolar)
    #     self.total_gastos_quetzales = total_quetzal
    #     self.total_gastos_dolares = total_dolar
    #     self.update({'total_gastos_quetzales': round(total_quetzal,4),'total_gastos_dolares': round(total_dolar,4)})

    @api.multi
    def calcular_impuesto(self):
        if self.prorrateo_impuesto:
            total_gt = 0
            total_usd = 0
            for linea in self.prorrateo_impuesto:
                total_q = 0
                logging.warn(linea.valor_dolar)
                if linea.documento_ids:
                    for d in linea.documento_ids:
                        if d.factura:
                            total_q += d.subtotal
                        else:
                            total_q += d.total

                linea.valor_quetzal = total_q
                linea.valor_dolar = round(linea.valor_quetzal / self.tipo_cambio,4)

                total_gt += linea.valor_quetzal
                total_usd += linea.valor_dolar

            self.total_gastos_quetzales = total_gt
            self.total_gastos_dolares = total_usd
            self.write({'state':'gastos'})
        return True

    @api.multi
    def generar_lineas_compra(self):
        total_impuesto_dolares = 0
        total_por_item = 0
        for linea in self.prorrateo_impuesto:
            total_impuesto_dolares += linea.valor_dolar
        for compra in self.compra_ids:
            suma_total_item = 0
            for linea in compra.order_line:
                suma_total_item +=linea.price_total / (self.euros_a_dolar)
            for linea in compra.order_line:
                descuento = round(linea.price_unit * (1 - linea.discount / 100),4)
                descuento2 = (linea.precio_original * linea.discount/100) if linea.discount > 0 else 0
                precio_euros = linea.precio_original if descuento else linea.price_unit
                total_item = linea.price_total / (self.euros_a_dolar)
                porcentaje = (total_item / suma_total_item)*100
                gastos_item = (porcentaje/100) * total_impuesto_dolares
                costo_item = gastos_item +total_item
                costo_unidad = costo_item / linea.product_qty
                costo_por_unidad_q = costo_unidad * self.tipo_cambio
                costo_bodega = costo_por_unidad_q * linea.product_qty
                precio_unitario_iva = costo_por_unidad_q * 1.12

                linea = {
                    'prorrateo_id':self.id,
                    'product_id': linea.product_id.id,
                    'cantidad': linea.product_qty,
                    'precio_euros': linea.precio_original if descuento > 0 else linea.price_unit,
                    'descuento': descuento2 if descuento2 > 0 else 0,
                    'precio_compra': descuento if linea.discount > 0 else linea.price_unit,
                    'total_euros': linea.price_total,
                    'total_item': total_item,
                    'porcentaje': porcentaje,
                    'gastos_item': gastos_item,
                    'costo_item': costo_item,
                    'costo_unidad': costo_unidad,
                    'costo_por_unidad_q': costo_por_unidad_q,
                    'costo_bodega': costo_bodega,
                    'precio_unitario_iva': precio_unitario_iva

                }

                linea_prorrateo = self.env['purchase.prorrateo_line'].create(linea)
                total_por_item += total_item
        self.total_por_item = total_por_item
        self.write({'state':'prorrateado'})

    @api.multi
    def asignar_costo(self):
        if self.compra_prorrateo_linea:
            self.write({'state':'costo'})
        return True

class PurchaseProrrateoLinea(models.Model):
    _name = "purchase.prorrateo_line"

    prorrateo_id = fields.Many2one('purchase.prorrateo','Prorrateo')
    product_id = fields.Many2one('product.product',string="Producto")
    cantidad = fields.Float('Cantidad')
    precio_euros = fields.Float('Precio EUR')
    descuento = fields.Float('Descuento')
    precio_compra = fields.Float('Precio Compra')
    total_euros = fields.Float('Total EUR')
    total_item = fields.Float('Total por ITEM')
    porcentaje = fields.Float('%')
    gastos_item = fields.Float('Gastos por item')
    costo_item = fields.Float('Costo total por item')
    costo_unidad = fields.Float('Costo total por unidad')
    costo_por_unidad_q = fields.Float('Costo por unidad')
    costo_bodega = fields.Float('Costo total en bodega')
    precio_unitario_iva = fields.Float('Precio unitario con iva')

class PurchaseProrrateoLinea(models.Model):
    _name = "purchase.prorrateo_impuesto"

    prorrateo_id = fields.Many2one('purchase.prorrateo','Prorrateo')
    impuesto_id = fields.Many2one('account.tax','Impuesto')
    valor_quetzal = fields.Float('Monto Q',default= 0,digits = (12,4))
    valor_dolar = fields.Float('Monto $',default = 0,digits = (12,4))
    documento_ids = fields.One2many('purchase.documento','linea_impuesto_id','Documentos')


class PurchaseDocumento(models.Model):
    _name = "purchase.documento"
    _rec_name = "numero"

    linea_impuesto_id = fields.Many2one('purchase.prorrateo_impuesto','Linea')
    numero = fields.Char('Número')
    fecha = fields.Date('Fecha')
    moneda_id = fields.Many2one('res.currency','Moneda')
    euros_a_dolar = fields.Float('Euro a Dolar')
    dolar_a_quetzal = fields.Float('Dolar a Quetzal')
    proveedor_id = fields.Many2one('res.partner','Proveedor')
    linea_ids = fields.One2many('purchase.documento_linea','documento_id','Lineas')
    total = fields.Float('Total')
    subtotal = fields.Float('Subtotal')
    factura = fields.Boolean('Factura')


    @api.onchange('linea_ids')
    def change_lineas(self):
        total = 0
        subtotal = 0
        for linea in self.linea_ids:
            total += round(linea.total,4)
            subtotal += round(linea.subtotal,4)
        self.update({'total': round(total,4),'subtotal':round(subtotal,4) })

class PurchaseDocumentoLinea(models.Model):
    _name = "purchase.documento_linea"

    documento_id = fields.Many2one('purchase.documento','Documento')
    product_id = fields.Many2one('product.template','Producto')
    subtotal = fields.Float('Subtotal')
    total_euro = fields.Float('Total euro')
    total_dolar = fields.Float('Total dolar')
    total = fields.Float('total')

    @api.onchange('total','total_euro','total_dolar','product_id')
    def change_total(self):
        if self.total_euro > 0:
            self.total_dolar = self.total_euro / self.documento_id.euros_a_dolar
        if self.total_dolar > 0:
            self.total = self.total_dolar * self.documento_id.dolar_a_quetzal
        if self.total > 0 and self.product_id.supplier_taxes_id:
            self.subtotal = self.total/1.12
        if self.total > 0 and self.documento_id.euros_a_dolar > 0:
            self.subtotal = self.total
    # def _get_monto(self):
    #     for linea in self:
    #         linea.valor_quetzal = linea.valor_dolar * self.prorrateo_id.tipo_cambio
