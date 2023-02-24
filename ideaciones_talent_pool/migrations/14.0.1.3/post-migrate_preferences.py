# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Insert res_preference_contact
    # cr.execute("INSERT INTO res_preference_contact (name) VALUES('Teléfono'),('Correo'),"
    #           "('Telegram'),('Linkedin'),('Zoom')")
    cr.execute("UPDATE res_partner SET type_partner='internal' WHERE type_partner is null")
    cr.execute("ALTER TABLE res_partner ADD COLUMN welcome integer")
    cr.execute("UPDATE res_partner SET welcome=0")




