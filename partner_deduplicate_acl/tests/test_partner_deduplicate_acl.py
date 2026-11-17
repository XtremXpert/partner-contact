# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, exceptions
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPartnerDeduplicateAcl(BaseCommon):
    # The merge wizard is restricted to the partner managers in Odoo 20.
    _test_user_groups = ("base.group_user", "base.group_partner_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Partner 1",
                "email": "partner1@example.org",
            }
        )
        cls.partner_2 = cls.partner_1.copy()
        cls.partner_2.write({"name": "Partner 1", "email": "partner2@example.org"})
        cls.user = new_test_user(
            cls.env,
            login="test_crm_deduplicate_acl",
            email="partner_deduplicate_acl@example.org",
            groups="base.group_partner_manager",
        )
        cls.wizard = cls.env["base.partner.merge.automatic.wizard"].create(
            {"group_by_name": True}
        )

    def test_same_email_restriction(self):
        wizard = self.wizard.with_user(self.user)
        wizard.action_start_manual_process()
        with self.assertRaises(exceptions.UserError):
            wizard.action_merge()
        self.user.sudo().group_ids = [
            Command.link(self.env.ref("partner_deduplicate_acl.group_unrestricted").id)
        ]
        # Now there shouldn't be error
        wizard = self.wizard.with_user(self.user)
        wizard.action_merge()
