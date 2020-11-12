# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import time
import base64
import logging
from datetime import date
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime
import xlsxwriter
import io

class prorrateo_wizard(models.TransientModel):
    _name = 'sta.prorrateo.wizard'

    prorrateo_id = fields.Many2one('purchase.prorrateo', 'Prorrateo', default=lambda self: self.env['purchase.prorrateo'].browse(self._context.get('active_id')), required=True)
    archivo = fields.Binary('Archivo')
    name =  fields.Char('File Name', size=32)

    # @api.multi
    # def print_report(self):
    #     datas = {'ids': self.env.context.get('active_ids', [])}
    #     # res = self.read(['igss','general','nomina_id'])
    #     res = res and res[0] or {}
    #     datas['form'] = res
    #     return self.env.ref('sta.action_prorrateo').report_action([], data=datas)


    def reporte_excel(self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            nomina = [w.nomina_id.id]
            res_nomina = self.env['report.hr_gt.planilla'].resumen(nomina,w.igss,w.general)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})

            hoja = libro.add_worksheet('reporte')

            hoja.write(0, 0, self.env.user.company_id.id)
            hoja.write(0, 1, w.nomina_id.name)
            hoja.write(0, 7 , 'Periodo')
            logging.warn(w.nomina_id.date_start)
            hoja.write(0, 8, w.nomina_id.date_start, formato_fecha)
            hoja.write(0, 9, w.nomina_id.date_end, formato_fecha)

            linea = 2
            num = 1
            merge_format = libro.add_format({'align': 'center'})

            # hoja.merge_range(5, 1, 6, 4, 'SALARIO', merge_format)
            total_neto = 0
            for l in res_nomina:
                if len(l['nominas']) > 0:
                    logging.warn('prrueba')
                    cell_format = libro.add_format({'bold': True})
                    hoja.write(linea, 0, l['nombre'],cell_format)
                    linea += 1
                    hoja.merge_range(linea, 1, linea, 4, 'SALARIO', merge_format)
                    hoja.merge_range(linea, 5, linea, 8, 'DIAS', merge_format)
                    hoja.merge_range(linea, 9, linea, 14, 'DEVENGADO', merge_format)
                    hoja.merge_range(linea, 15, linea, 21, 'DESCUENTOS', merge_format)
                    hoja.write(linea, 22, 'TOTAL')
                    linea += 1
                    hoja.write(linea, 0, 'Nombrel del empleado')
                    hoja.write(linea, 1, 'Salario base')
                    hoja.write(linea, 2, 'Bonificacion')
                    hoja.write(linea, 3, 'Bono otro')
                    hoja.write(linea, 4, 'Total')
                    hoja.write(linea, 5, 'Trabajado')
                    hoja.write(linea, 6, 'Vacas')
                    hoja.write(linea, 7, 'Faltas')
                    hoja.write(linea, 8, 'Susp')
                    hoja.write(linea, 9, 'Sueldo')
                    hoja.write(linea, 10, 'Vacaciones')
                    hoja.write(linea, 11, 'Bonificacion decreto 37-2001')
                    hoja.write(linea, 12, 'Otro bono')
                    hoja.write(linea, 13, 'Comisión')
                    hoja.write(linea, 14, 'TOTAL')
                    hoja.write(linea, 15, 'IGSS')
                    hoja.write(linea, 16, 'ISR')
                    hoja.write(linea, 17, 'UNIFORMES')
                    hoja.write(linea, 18, 'OTROS DESCUENTOS')
                    hoja.write(linea, 19, 'VALES')
                    hoja.write(linea, 20, 'ANTICIPO QUINCENA')
                    hoja.write(linea, 21, 'TOTAL')
                    hoja.write(linea, 22, 'LIQUIDO')
                    total_departamento = 0
                    for nomina in l['nominas']:
                        linea+= 1
                        logging.warn(nomina['nombre_empleado'])
                        hoja.write(linea, 0, nomina['nombre_empleado'])
                        hoja.write(linea, 1, nomina['base'])
                        hoja.write(linea, 2, nomina['bonificacion'])
                        hoja.write(linea, 3, nomina['bono_otro'])
                        hoja.write(linea, 4, nomina['total_sueldo'])
                        hoja.write(linea, 5, nomina['trabajado'])
                        hoja.write(linea, 6, nomina['vacas'])
                        hoja.write(linea, 7, nomina['faltas'])
                        hoja.write(linea, 8, nomina['suspension'])
                        hoja.write(linea, 9, nomina['sueldo'])
                        hoja.write(linea, 10, nomina['vacaciones'])
                        hoja.write(linea, 11, nomina['bonificacion'])
                        hoja.write(linea, 12, nomina['bono_otro'])
                        hoja.write(linea, 13, nomina['comision'])
                        hoja.write(linea, 14, nomina['total'])
                        hoja.write(linea, 15, nomina['igss'])
                        hoja.write(linea, 16, nomina['isr'])
                        hoja.write(linea, 17, nomina['uniformes'])
                        hoja.write(linea, 18, nomina['otros_descuentos'])
                        hoja.write(linea, 19, nomina['vales'])
                        hoja.write(linea, 20, nomina['quincena_anterior'])
                        hoja.write(linea, 21, nomina['total_descuentos'])
                        hoja.write(linea, 22,round(nomina['total_liquido'],4),cell_format)
                        total_neto += nomina['total_liquido']
                        total_departamento += round(nomina['total_liquido'],4)

                    linea += 1
                    logging.warn(total_departamento)
                    hoja.write(linea, 22, round(total_departamento,4),cell_format)


                    linea +=2

            hoja.write(linea, 0, 'TOTAL PLANILLA')
            hoja.write(linea, 1, total_neto,cell_format)
            # totales = []
            # columna = 6
            # for c in w.planilla_id.columna_id:
            #     hoja.write(linea, columna, c.name)
            #     columna += 1
            #     totales.append(0)
            # totales.append(0)
            #
            # hoja.write(linea, columna, 'Liquido a recibir')
            # hoja.write(linea, columna+1, 'Banco a depositar')
            # hoja.write(linea, columna+2, 'Cuenta a depositar')
            # hoja.write(linea, columna+3, 'Observaciones')
            # hoja.write(linea, columna+4, 'Cuenta analítica')

            # linea += 1
            # for l in w.nomina_id.slip_ids:
            #     dias = 0
            #     total_salario = 0
            #
            #     hoja.write(linea, 0, num)
            #     hoja.write(linea, 1, l.employee_id.codigo_empleado)
            #     hoja.write(linea, 2, l.employee_id.name)
            #     hoja.write(linea, 3, l.contract_id.date_start,formato_fecha)
            #     hoja.write(linea, 4, l.employee_id.job_id.name)
            #     work = -1
            #     trabajo = -1
            #     for d in l.worked_days_line_ids:
            #         if d.code == 'TRABAJO100':
            #             trabajo = d.number_of_days
            #         elif d.code == 'WORK100':
            #             work = d.number_of_days
            #     if trabajo >= 0:
            #         dias += trabajo
            #     else:
            #         dias += work
            #     hoja.write(linea, 5, dias)
            #
            #     columna = 6
            #     for c in w.planilla_id.columna_id:
            #         reglas = [x.id for x in c.regla_id]
            #         entradas = [x.name for x in c.entrada_id]
            #         total_columna = 0
            #         for r in l.line_ids:
            #             if r.salary_rule_id.id in reglas:
            #                 total_columna += r.total
            #         for r in l.input_line_ids:
            #             if r.name in entradas:
            #                 total_columna += r.amount
            #         if c.sumar:
            #             total_salario += total_columna
            #         totales[columna-6] += total_columna
            #
            #         hoja.write(linea, columna, total_columna)
            #         columna += 1
            #
            #     totales[columna-6] += total_salario
            #     hoja.write(linea, columna, total_salario)
            #     hoja.write(linea, columna+1, l.employee_id.bank_account_id.bank_id.name)
            #     hoja.write(linea, columna+2, l.employee_id.bank_account_id.acc_number)
            #     hoja.write(linea, columna+3, l.note)
            #     if l.move_id and len(l.move_id.line_ids) > 0 and l.move_id.line_ids[0].analytic_account_id:
            #         if l.move_id.line_ids[0].analytic_account_id:
            #             hoja.write(linea, columna+4, l.move_id.line_ids[0].analytic_account_id.name)
            #         else:
            #             hoja.write(linea, columna+4, 'indefinido')
            #     else:
            #         if l.contract_id.analytic_account_id.name:
            #             hoja.write(linea, columna+4, l.contract_id.analytic_account_id.name)
            #         else:
            #             hoja.write(linea, columna+4, 'indefinido')
            #     linea += 1
            #     num += 1
            #
            # columna = 6
            # for t in totales:
            #     hoja.write(linea, columna, totales[columna-6])
            #     columna += 1

            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'prorrateo.xls'})
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sta.prorrateo.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
