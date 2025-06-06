from odoo import fields, models, api
from datetime import datetime


class Ausentismo(models.Model):
    _name = 'dtm.rh.ausentismo'
    _description = 'Modelo para llevar el control del ausentismo del persona'

    no_month = fields.Integer()
    mes_nombre = fields.Char(string='Mes')
    dias_laborados = fields.Integer(string="Dias")
    faltas = fields.Integer(string="Faltas")
    empleados = fields.Integer(string="No Empleados")
    porcentaje = fields.Float(string="%")

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Ausentismo, self).get_view(view_id, view_type, **options)

        for month in range(1, 13):
            if month <= int(datetime.today().strftime("%m")):
                # Busca las cotizaciones del mes actual y del mes pasado
                self.env.cr.execute(
                    " SELECT fecha, asistencias,faltas,feriado  FROM dtm_ano_laboral WHERE EXTRACT(MONTH FROM fecha) = " + str(month) +
                    " AND EXTRACT(YEAR FROM fecha) = " + datetime.today().strftime("%Y") + ";")
                get_proceso = self.env.cr.fetchall()
                faltas = 0
                feriado = 0
                personal_list = []
                nombre_mes = ''
                if get_proceso:
                    # Se calcula los días laborados
                    for personal in get_proceso:
                        faltas += personal[2]
                        feriado += max(personal[3],0)
                        personal_list = self.env['dtm.ano.laboral'].search([('fecha','=',personal[0])]).personal_id.mapped('nombre')
                        nombre_mes = str(personal[0].strftime("%B")).capitalize()

                # Si el mes existe lo actualiza si no lo crea
                get_this = self.env['dtm.rh.ausentismo'].search([('no_month', '=', month)])
                if get_this:
                    get_this.write({
                        'no_month':month,
                        'mes_nombre':nombre_mes,
                        'dias_laborados':len(get_proceso)-feriado,
                        'faltas':faltas,
                        'empleados':len(list(set(personal_list))),
                        'porcentaje':(faltas * 100)/max(((len(get_proceso)-feriado) * len(list(set(personal_list)))),1),
                    })
                else:
                    get_this.create({
                        'no_month':month,
                        'mes_nombre': nombre_mes,
                        'dias_laborados':len(get_proceso)-feriado,
                        'faltas':faltas,
                        'empleados':len(list(set(personal_list))),
                        'porcentaje':(faltas * 100)/max((len(get_proceso)-feriado * len(list(set(personal_list)))),1),
                    })
        return res


class Rotacion(models.Model):
    _name = 'dtm.rh.rotacion'
    _description = 'Modelo para llevar el control de la rotación'

    no_month = fields.Integer()
    mes_nombre = fields.Char(string='Mes')
    mes = fields.Date()
    empleados_init = fields.Integer(string="No Empleados Inicio")
    empleados_fin = fields.Integer(string="No Empleados Final")
    bajas = fields.Integer(string="Bajas")
    porcentaje = fields.Float(string="%")

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Rotacion, self).get_view(view_id, view_type, **options)

        for month in range(1, 13):
            if month <= int(datetime.today().strftime("%m")):
                # Busca las cotizaciones del mes actual y del mes pasado
                self.env.cr.execute(
                    " SELECT fecha, asistencias  FROM dtm_ano_laboral WHERE EXTRACT(MONTH FROM fecha) = " + str(
                        month) +
                    " AND EXTRACT(YEAR FROM fecha) = " + datetime.today().strftime("%Y") + ";")
                get_proceso = self.env.cr.fetchall()
                mes = datetime.today()
                personal_list = {}
                nombre_mes = ''
                if get_proceso:
                    # Se calculan los días laborados
                    for personal in get_proceso:
                        personal_list[personal[0].strftime("%d")] = self.env['dtm.ano.laboral'].search([('fecha','=',personal[0])]).personal_id.mapped('nombre')
                        nombre_mes = str(personal[0].strftime("%B")).capitalize()
                personal_list = dict(sorted(personal_list.items()))
                # Si el mes existe lo actualiza si no lo crea
                get_this = self.env['dtm.rh.rotacion'].search([('no_month', '=', month)])
                # Se recolecta la lista de empleados del primer y último día del mes
                empleados_init = list(personal_list.values())[0] if personal_list else ''
                empleados_fin = list(personal_list.values())[-1] if personal_list else ''
                print(nombre_mes)
                print('empleados_init',len(empleados_init),empleados_init)
                print('empleados_fin',len(empleados_fin),empleados_fin)

                # Se obtiene el Número promedio de empleados
                promedio_empleados = max(((len(empleados_fin)+len(empleados_init))/2),1)
                bajas = 0
                if empleados_init != empleados_fin:
                    for empleado in empleados_init:
                        if empleado not in empleados_fin:
                            bajas+=1
                print('promedio_empleados',promedio_empleados)
                print('bajas',bajas)
                print('resultado',(bajas*100)/promedio_empleados)
                if get_this:
                    get_this.write({
                        'no_month': month,
                        'mes_nombre': nombre_mes,
                        'mes': mes,
                        'empleados_init': len(empleados_init),
                        'empleados_fin': len(empleados_fin),
                        'bajas':bajas,
                        'porcentaje':(bajas*100)/promedio_empleados,
                    })
                else:
                    get_this.create({
                        'no_month': month,
                        'mes_nombre': nombre_mes,
                        'mes': mes,
                        'empleados_init': len(empleados_init),
                        'empleados_fin': len(empleados_fin),
                        'bajas': bajas,
                        'porcentaje': (bajas*100)/promedio_empleados,
                    })
        return res