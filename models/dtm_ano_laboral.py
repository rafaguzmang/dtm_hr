from odoo import fields, models, api
from datetime import datetime,timedelta



class Laboral(models.Model):
    _name = 'dtm.ano.laboral'
    _description = 'Modelo para llevar las asistencias de los días trabajados'
    _rec_name = "fecha"
    _order = "dia desc"
    # Obtiene el nuveno día
    def obtener_dia(self):
        get_udia = self.env['dtm.ano.laboral'].search([],limit=1,order='dia desc')
        # Convierte el día del año en data
        ano_actual = datetime.now().strftime('%Y')
        fecha_inicial = datetime(int(ano_actual), 1, 1)  # Primer día del año
        fecha_resultante = fecha_inicial + timedelta(days=get_udia.dia)
        if fecha_resultante.strftime("%A") == 'domingo':
            return get_udia.dia + 2
        return get_udia.dia + 1
    # Obtiene la fecha partiendo del día del año
    def obtener_fecha(self):
        anio = datetime.now().year
        get_udia = self.env['dtm.ano.laboral'].search([],limit=1,order='dia desc')
         # Convierte el día del año en data
        ano_actual = datetime.now().strftime('%Y')
        fecha_inicial = datetime(int(ano_actual), 1, 1)  # Primer día del año
        fecha_resultante = fecha_inicial + timedelta(days=get_udia.dia)
        if fecha_resultante.strftime("%A") == 'domingo':
            return datetime.strptime(f"{anio} {get_udia.dia + 2}", "%Y %j").date()
        return datetime.strptime(f"{anio} {get_udia.dia + 1}", "%Y %j").date()

    dia = fields.Integer(string='Día',default=obtener_dia,readonly=True)
    fecha = fields.Date(string='Fecha',default= obtener_fecha,readonly=True)
    asistencias = fields.Integer(string='Asistencias',readonly=True,compute= '_compute_asistencia',store=True)
    faltas = fields.Integer(string='Faltas',readonly=True)
    permisos = fields.Integer(string='Permisos',readonly=True)
    vacaciones = fields.Integer(string='Vacaciones',readonly=True)
    retardos = fields.Integer(string='Retardos',readonly=True)
    feriado = fields.Boolean()

    personal_id = fields.One2many('dtm.hr.personal','model_id');

    # Botón para cargar la tabla con todo el personal activo
    def action_cargar(self):
        get_personal = self.env['dtm.hr.empleados'].search([])
        for persona in get_personal:
            if not self.env['dtm.hr.personal'].search([('nombre','=',persona.nombre),('dia','=',self.dia)]):
                vacaciones = self.env['dtm.hr.personal'].search([('nombre','=',persona.nombre),('dia','=',self.dia-1)])
                self.env['dtm.hr.personal'].create({
                    'nombre':persona.nombre,
                    'asistencia':'si',
                    'dia':self.dia,
                    'vacaciones':True if vacaciones.vacaciones else ''
                })
                # Obtiene el día anterior y revisa si tiene periodo de vacaciones
                if vacaciones.vacaciones:
                    fecha_obj = datetime.strptime(str(vacaciones.periodo_final), "%Y-%m-%d")
                    dia_ano = fecha_obj.timetuple().tm_yday
                    if self.dia <= dia_ano:
                        self.env['dtm.hr.personal'].search([('nombre','=',persona.nombre),('dia','=',self.dia)]).write({
                            'asistencia':False,
                            'vacaciones':True,
                            'periodo_inicio':vacaciones.periodo_inicio,
                            'periodo_final':vacaciones.periodo_final,
                        })
                    else:
                        self.env['dtm.hr.personal'].search([('nombre','=',persona.nombre),('dia','=',self.dia)]).write({
                            'asistencia':'si',
                            'vacaciones':False,
                            'periodo_inicio':False,
                            'periodo_final':False,
                        })
            else:
                # Obtiene el día anterior y revisa si tiene periodo de vacaciones
                vacaciones = self.env['dtm.hr.personal'].search([('nombre','=',persona.nombre),('dia','=',self.dia-1)])
                if vacaciones.vacaciones:
                    fecha_obj = datetime.strptime(str(vacaciones.periodo_final), "%Y-%m-%d")
                    dia_ano = fecha_obj.timetuple().tm_yday
                    if self.dia <= dia_ano:
                        self.env['dtm.hr.personal'].search([('nombre','=',persona.nombre),('dia','=',self.dia)]).write({
                            'asistencia':False,
                            'vacaciones':True,
                            'periodo_inicio':vacaciones.periodo_inicio,
                            'periodo_final':vacaciones.periodo_final,
                        })
                    else:
                        self.env['dtm.hr.personal'].search([('nombre','=',persona.nombre),('dia','=',self.dia)]).write({
                            'asistencia':'si',
                            'vacaciones':False,
                            'periodo_inicio':False,
                            'periodo_final':False,
                        })


        self.personal_id = [(5,0,0)]
        self.personal_id = [(6,0,self.env['dtm.hr.personal'].search([('dia','=',self.dia)]).mapped('id'))]

    #Calcula las estadisticas del personal
    @api.depends('personal_id')
    def _compute_asistencia(self):
        for result in self:
            # get_asistencias = result.personal_id.search('asistencia','=','si').mapped('id')
            get_asistencias = result.personal_id
            asistencias = 0
            faltas = 0
            vacaciones = 0
            permiso = 0
            for persona in get_asistencias:
                if persona.vacaciones == True and not persona.periodo_inicio  and not   persona.periodo_final:
                    persona.write({'asistencia':'','periodo_inicio':datetime.today(),'periodo_final':datetime.today()})
                elif persona.vacaciones == False:
                    persona.write({'periodo_inicio':'','periodo_final':''})

                if persona.vacaciones:
                    vacaciones += 1
                if persona.permiso > 0:
                    permiso += 1
                if persona.asistencia == 'si':
                    asistencias += 1
                elif persona.asistencia == 'no':
                    faltas += 1

            result.asistencias = asistencias
            result.faltas = faltas
            result.vacaciones = vacaciones
            result.permisos = permiso

    def action_pasive(self):
        pass

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Laboral, self).get_view(view_id, view_type, **options)
        # Rotación
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
                        personal_list[personal[0].strftime("%d")] = self.env['dtm.ano.laboral'].search(
                            [('fecha', '=', personal[0])]).personal_id.mapped('nombre')
                        nombre_mes = str(personal[0].strftime("%B")).capitalize()
                personal_list = dict(sorted(personal_list.items()))
                # Si el mes existe lo actualiza si no lo crea
                get_this = self.env['dtm.rh.rotacion'].search([('no_month', '=', month)])
                # Se recolecta la lista de empleados del primer y último día del mes
                empleados_init = list(personal_list.values())[0] if personal_list else ''
                empleados_fin = list(personal_list.values())[-1] if personal_list else ''
                print(nombre_mes)
                print('empleados_init', len(empleados_init), empleados_init)
                print('empleados_fin', len(empleados_fin), empleados_fin)

                # Se obtiene el Número promedio de empleados
                promedio_empleados = max(((len(empleados_fin) + len(empleados_init)) / 2), 1)
                bajas = 0
                if empleados_init != empleados_fin:
                    for empleado in empleados_init:
                        if empleado not in empleados_fin:
                            bajas += 1
                print('promedio_empleados', promedio_empleados)
                print('bajas', bajas)
                print('resultado', (bajas * 100) / promedio_empleados)
                if get_this:
                    get_this.write({
                        'no_month': month,
                        'mes_nombre': nombre_mes,
                        'mes': mes,
                        'empleados_init': len(empleados_init),
                        'empleados_fin': len(empleados_fin),
                        'bajas': bajas,
                        'porcentaje': (bajas * 100) / promedio_empleados,
                    })
                else:
                    get_this.create({
                        'no_month': month,
                        'mes_nombre': nombre_mes,
                        'mes': mes,
                        'empleados_init': len(empleados_init),
                        'empleados_fin': len(empleados_fin),
                        'bajas': bajas,
                        'porcentaje': (bajas * 100) / promedio_empleados,
                    })

        # Ausentismo
        for month in range(1, 13):
            if month <= int(datetime.today().strftime("%m")):
                # Busca las cotizaciones del mes actual y del mes pasado
                self.env.cr.execute(
                    " SELECT fecha, asistencias,faltas,feriado  FROM dtm_ano_laboral WHERE EXTRACT(MONTH FROM fecha) = " + str(
                        month) +
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
                        feriado += max(personal[3], 0)
                        personal_list = self.env['dtm.ano.laboral'].search(
                            [('fecha', '=', personal[0])]).personal_id.mapped('nombre')
                        nombre_mes = str(personal[0].strftime("%B")).capitalize()

                # Si el mes existe lo actualiza si no lo crea
                get_this = self.env['dtm.rh.ausentismo'].search([('no_month', '=', month)])
                if get_this:
                    get_this.write({
                        'no_month': month,
                        'mes_nombre': nombre_mes,
                        'dias_laborados': len(get_proceso) - feriado,
                        'faltas': faltas,
                        'empleados': len(list(set(personal_list))),
                        'porcentaje': (faltas * 100) / max(
                            ((len(get_proceso) - feriado) * len(list(set(personal_list)))), 1),
                    })
                else:
                    get_this.create({
                        'no_month': month,
                        'mes_nombre': nombre_mes,
                        'dias_laborados': len(get_proceso) - feriado,
                        'faltas': faltas,
                        'empleados': len(list(set(personal_list))),
                        'porcentaje': (faltas * 100) / max((len(get_proceso) - feriado * len(list(set(personal_list)))), 1),
                    })
        return res



class Personal(models.Model):
    _name = 'dtm.hr.personal'
    _description = 'Modelo para llevar el registro del personal'

    model_id = fields.Many2one('dtm.ano.laboral')
    nombre = fields.Char(string='Nombre')
    asistencia = fields.Selection(string="Asistencia",  selection=[("no","No"),("si","Si")])
    retardo = fields.Float(string='Retardo/hr')
    permiso = fields.Float(string='Permiso/hr')
    vacaciones = fields.Boolean(string='Vacaciones')
    periodo_inicio = fields.Date(string='Inicio')
    periodo_final = fields.Date(string='final')
    dia = fields.Integer()





