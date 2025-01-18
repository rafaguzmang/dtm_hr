from odoo import api,models,fields
from datetime import datetime

class Empleados(models.Model):
    _name = "dtm.hr.empleados"
    _description = "Registro de asistencias"
    _rec_name = "nombre"
    _order = "nombre asc"

    nombre = fields.Char(string='Nombre Completo')
    ingreso = fields.Date(string='Fecha de ingreso')

    # Botón para dar de baja al personal
    def action_baja(self):
        get_bajas = self.env['dtm.hr.bajas'].search([('nombre','=',self.nombre)])
        if not get_bajas:
            get_bajas.create({
                'nombre': self.nombre,
                'salida': datetime.now()  # Fecha actual para registrar la baja
            })
            self.env['dtm.hr.empleados'].search([('nombre','=',self.nombre)]).unlink()

class Exempleados(models.Model):
    _name = "dtm.hr.bajas"
    _description = "Registro de bajas"
    _order = "nombre asc"
    _rec_name = "nombre"



    nombre = fields.Char(string='Nombre ')
    salida = fields.Date(string='Fecha de Baja')


    # Botón para dar de alta al personal después de su bajadef action_baja(self):
    def action_alta(self):
        get_bajas = self.env['dtm.hr.empleados'].search([('nombre','=',self.nombre)])
        if not get_bajas:
            get_bajas.create({
                'nombre': self.nombre,
                'ingreso': datetime.now()  # Fecha actual para registrar la baja
            })
            self.env['dtm.hr.bajas'].search([('nombre','=',self.nombre)]).unlink()


