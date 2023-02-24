from operator import itemgetter

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


# Param Value
class ParamValueExam(models.Model):
    _name = "order.param.value.exams"
    _description = "Valor del Parametro del examen"
    _order = "exam_type"

    name = fields.Char()
    exam_id = fields.Many2one(
        comodel_name="agend.medical.lab.exam",
        string="Examen",
        readonly=True,
        required=True,
    )
    exam_uom = fields.Char(related="exam_id.param_uom")
    exam_ref_value = fields.Html(related="exam_id.param_ref_value")
    exam_type = fields.Many2one(
        comodel_name="agend.name.lab.exam", string="Examen", related="exam_id.exam_id"
    )  # Type of exam ex: Examen de sangre
    param_value = fields.Char("Valor del parametro")
    order_id = fields.Many2one(
        comodel_name="order.exams.lab", string="Orden", required=False
    )

    # _sql_constraints
    _sql_constraints = [
        ('order_id_param_exam_uniq',
         'UNIQUE (exam_id, order_id)',
         'Los parametros a medir de la prueba son unicos para cada orden!')]


class OrderExams(models.Model):
    _name = "order.exams.lab"
    _description = "Orden de examenes al paciente"

    name = fields.Char(default="New")
    patient_id = fields.Many2one(
        comodel_name="res.partner", string="Paciente", required=True
    )
    doctor_id = fields.Many2one(
        comodel_name="res.partner", string="Médico", required=True
    )
    lab_exam_ids = fields.Many2many(
        comodel_name="agend.medical.lab.exam", string="Examenes de la Orden"
    )
    for_process = fields.Boolean(
        string="Listo para procesar", default=False, required=False
    )
    result_lines_ids = fields.One2many(
        comodel_name="order.param.value.exams",
        inverse_name="order_id",
        string="Lista de Resultados",
        required=False,
    )
    observations = fields.Text(string="Observaciones", required=False)
    order_ids = fields.One2many(
        "account.move", "order_lab_id", string="Quotation Order"
    )
    order_count = fields.Integer(compute="_get_orders_count", store=True)

    def _default_company(self):
        """Return user company id"""
        company_id = self.env['res.company'].search([('parent_id', '=', False)], limit=1)
        return company_id.id

    order_company = fields.Many2one(
        comodel_name="res.company", string="Company", required=True, readonly=True,
        default=_default_company,
    )

    @api.depends('order_ids')
    def _get_orders_count(self):
        for item in self:
            if item.order_ids:
                item.order_count = len(item.order_ids)
            else:
                item.order_count = 0

    def action_ready_to_process(self):
        self.for_process = True
        self.create_params_lines()

    def create_params_lines(self):
        """Se generan las lineas de parametros de las pruebas
        al pulsar el boton ready_to_process
        segun la lista de examenes elegidos"""
        Param = self.env["order.param.value.exams"]
        if self.lab_exam_ids and self.for_process:
            _logger.info("INFO ORDER %s" % self.lab_exam_ids)
            order_2category = sorted(self.lab_exam_ids, key=lambda car: car['category_id'])
            order_2exams = sorted(order_2category, key=lambda car: car['exam_id'])
            _logger.info("INFO ORDER EXAM 1 %s" % order_2exams)
            # order_exams2 = sorted(self.lab_exam_ids, key=itemgetter(4, 5))
            # _logger.info("INFO ORDER EXAM 2 %s" % order_exams2)
            for exam in self.lab_exam_ids:
                param_value = {
                    "name": exam.name,
                    "exam_id": exam.id,
                    "param_value": 0.00,
                    "order_id": self.id,
                }
                param_line = Param.create(param_value)
                self.result_lines_ids |= param_line

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("order.exams.lab") or "New"
            )
        result = super(OrderExams, self).create(vals)
        return result

    def send_msg_doctor(self):
        if self.doctor_id:
            presentation = "Estimado(a) Doctor " + self.doctor_id.name
            mobile = self.doctor_id.phone if self.doctor_id.phone else ""
            contact = self.doctor_id.id
            return self.send_msg(contact, mobile, presentation)
        else:
            raise ValidationError("Debe selecionar un Medico!")

    def send_msg_patient(self):
        if self.patient_id:
            presentation = "Estimado(a) paciente " + self.patient_id.name
            mobile = self.patient_id.phone if self.patient_id.phone else ""
            contact = self.patient_id.id
            return self.send_msg(contact, mobile, presentation)
        else:
            raise ValidationError("Debe selecionar un Paciente!")

    def send_msg(self, contact, mobile, presentation):
        message = "se adjuntan los resultados del examen solicitado "
        attach = "orden No. " + self.name + " Saludos."
        return {
            "type": "ir.actions.act_window",
            "name": _("Whatsapp Message"),
            "res_model": "whatsapp.lab.message.wizard",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": {
                "default_user_id": contact,
                "default_mobile": mobile,
                "default_message": f"{presentation, message, attach}",
            },
        }

    def action_sale_quotations_new(self, context=None):
        if self.patient_id:
            context = {
                "default_order_lab_id": self.id,
                "default_partner_id": self.patient_id.id,
                "default_move_type": "out_invoice",
                "default_invoice_date": fields.Datetime.today(),
            }
            return {
                "name": _("Invoice"),
                "view_mode": "form",
                "view_id": False,
                "view_type": "form",
                "res_model": "account.move",
                "type": "ir.actions.act_window",
                "nodestroy": True,
                "target": "current",
                "context": context,
            }
        else:
            raise ValidationError("Debe seleccionar un Paciente para la facturacion!")

    def return_action_view_orders(self):
        """This opens the xml action view for orders"""
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "agendmedic.medical_invoice_action_quotations"
        )
        action["context"] = {
            "default_medical_record_id": self.id,
        }
        return action
