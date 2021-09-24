# coding: utf-8
from odoo.tests.common import TransactionCase

class TestResPartner(TransactionCase):

    #test_compute_profile_status
    def test_compute_profile_status(self):
        test_partner_1 = self.env['res.partner'].create(
            {
                'name': 'Some Client Test',
                'linkedin_account': 'https://linkedin.com/in/someClient-237872',
            }
        )
        test_partner_1.compute_profile_status()
        self.assertEqual(test_partner_1.profile_status,False)
        test_partner_2 = self.env['res.partner'].create(
            {
                'name': 'Another Client Test',
                'linkedin_account': 'https://linkedin.com/in/Another-237872',
                'facebook_account': 'https://facebook.com/Another',
                'twitter_account': 'https://twitter.com/someClient',
            }
        )
        test_partner_2.compute_profile_status()
        self.assertEqual(test_partner_2.profile_status, True)


    #test for search filter by linkedin_account
    def test_name_search(self):
        test_partner_3 = self.env['res.partner'].create(
            {
                'name': 'Other Client Test',
                'linkedin_account': 'https://linkedin.com/in/OtherClient-237872',
            }
        )
        test_partner_4 = self.env['res.partner'].create(
            {
                'name': 'Another Client Test',
                'linkedin_account': '',
            }
        )
        ResPartner = self.env['res.partner']
        customer_1 = ResPartner.search([('linkedin_account','ilike','Other')])
        customer_2 = ResPartner.search([('linkedin_account', 'ilike', 'someClient')])
        self.assertEqual(test_partner_3,customer_1)
        self.assertFalse(customer_2)
        self.assertNotEqual(test_partner_4,test_partner_3)