from odoo import fields, models, api


# name
class NameLabExam(models.Model):
    _name = "agend.name.lab.exam"
    _description = "Nomenclador nombre del examen"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(
        string='Prioridad en la secuencia',
        default=0,
        required=True)


# category
class CatLabExam(models.Model):
    _name = "agend.cat.lab.exam"
    _description = "Nomenclador Categoria del examen"

    name = fields.Char()


# type
class TypeLabExam(models.Model):
    _name = "agend.type.lab.exam"
    _description = "Nomenclador tipo en el examen"

    name = fields.Char()


# lab test param
class LabTestParam(models.Model):
    _name = "agend.lab.test.param"
    _description = "Parametro de la prueba"

    name = fields.Char()
    param_uom = fields.Char("Unidad de medicion")
    ref_value = fields.Html("Valor referencial")


# Plantillas de Grupo de Pruebas
class MedicalLabExam(models.Model):
    _name = "agend.medical.lab.exam"
    _description = "Nomenclador Grupo de Prueba"
    _order = "exam_id,category_id"

    name = fields.Char(string="Nombre de la Prueba", required=True)
    parameter = fields.Many2one(
        comodel_name="agend.lab.test.param", string="Parametro a medir", required=True)
    param_uom = fields.Char(related="parameter.param_uom")
    param_ref_value = fields.Html(related="parameter.ref_value")
    exam_id = fields.Many2one(
        comodel_name="agend.name.lab.exam",
        string="Examen",
    )
    category_id = fields.Many2one(
        comodel_name="agend.cat.lab.exam", string="Categoría", required=False
    )
    cost = fields.Float("Costo")
    type_id = fields.Many2one(
        comodel_name="agend.type.lab.exam", string="Tipo", required=False
    )

    # _sql_constraints
    _sql_constraints = [
        ('order_id_param_exam_uniq',
         'UNIQUE (exam_id, order_id)',
         'Los parametros a medir de la prueba son unicos para cada orden!')]
