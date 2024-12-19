from odoo import api,models,fields

class Empleados(models.Model):
    _name = "dtm.hr.empleados"
    _description = "Registro de asistencias"
    _rec_name = "nombre"

    nombre = fields.Char(string='Nombre Completo')
    ingreso = fields.Date(string='Fecha de ingreso')


class Exempleados(models.Model):
    _name = "dtm.hr.bajas"
    _description = "Registro de bajas"

    nombre = fields.Char(string='Nombre ')
    salida = fields.Date(string='Fecha de Baja')





