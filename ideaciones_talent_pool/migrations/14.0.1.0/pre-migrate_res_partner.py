# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Add temporary credit product column
    cr.execute('ALTER TABLE res_partner ADD COLUMN sex character varying'
               ', ADD COLUMN whatsapp character varying'
               ', ADD COLUMN facebook character varying'
               ', ADD COLUMN orcid character varying'
               ', ADD COLUMN linkedin character varying'
               ', ADD COLUMN website_own character varying'
               ', ADD COLUMN sumary_cv text'
               ', ADD COLUMN speciality character varying'
               ', ADD COLUMN status_work text'
               ', ADD COLUMN job_name character varying'
               ', ADD COLUMN institution text'
               ', ADD COLUMN institution character varying'
               ', ADD COLUMN ministery text'
               ', ADD COLUMN preferences character varying')



