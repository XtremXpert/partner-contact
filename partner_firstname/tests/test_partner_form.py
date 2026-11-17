# Copyright 2015 Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""These tests try to mimic the behavior of the UI form.

The form operates in onchange mode, with its limitations.
"""

from odoo.tests import Form, TransactionCase

from ..exceptions import EmptyNamesError

# Odoo 20 dropped ``company_type``: a partner is a company when it has a VAT
# (see ``res.partner._compute_is_company``).
COMPANY_VAT = "BE0477472701"


class PartnerCompanyCase(TransactionCase):
    is_company = True

    def set_company(self, partner_form):
        if self.is_company:
            partner_form.vat = COMPANY_VAT

    def test_create_from_form(self):
        name = "Sôme company"
        with Form(self.env["res.partner"]) as partner_form:
            self.set_company(partner_form)
            partner_form.name = name

        self.assertEqual(partner_form.name, name)
        self.assertEqual(partner_form.firstname, False)
        self.assertEqual(partner_form.lastname, name)

    def test_create_from_form_keeps_name_over_default_name(self):
        """If the name is updated in the create dialog, it must be saved instead of the
        search term
        """
        with Form(
            self.env["res.partner"].with_context(default_name="Test")
        ) as partner_form:
            self.set_company(partner_form)
            partner_form.name = "Full Test"

        self.assertEqual(partner_form.name, "Full Test")
        self.assertEqual(partner_form.firstname, False)
        self.assertEqual(partner_form.lastname, "Full Test")

    def test_empty_name(self):
        """If we empty the name and save the form, EmptyNamesError must
        be raised (firstname and lastname are reset...)
        """
        with Form(self.env["res.partner"]) as partner_form:
            self.set_company(partner_form)

            name = "Foó"
            # User sets a name
            partner_form.name = name
            # call save to  trigger the inverse
            partner_form.save()
            self.assertEqual(partner_form.name, name)
            self.assertEqual(partner_form.firstname, False)
            self.assertEqual(partner_form.lastname, name)

            # User unsets name
            partner_form.name = ""
            # call save to  trigger the inverse and therefore raise an exception
            with self.assertRaises(EmptyNamesError), self.env.cr.savepoint():
                partner_form.save()

            name += " bis"
            partner_form.name = name
            partner_form.save()
            self.assertEqual(partner_form.name, name)
            self.assertEqual(partner_form.firstname, False)


class PartnerContactCase(PartnerCompanyCase):
    is_company = False

    def test_create_from_form_only_firstname(self):
        """A user creates a contact with only the firstname from the form."""
        firstname = "Fïrst"
        with Form(self.env["res.partner"]) as partner_form:
            self.set_company(partner_form)

            # Changes firstname, which triggers compute
            partner_form.firstname = firstname

        self.assertEqual(partner_form.lastname, False)
        self.assertEqual(partner_form.firstname, firstname)
        self.assertEqual(partner_form.name, firstname)

    def test_create_from_form_only_lastname(self):
        """A user creates a contact with only the lastname from the form."""
        lastname = "Läst"
        with Form(self.env["res.partner"]) as partner_form:
            self.set_company(partner_form)

            # Changes lastname, which triggers compute
            partner_form.lastname = lastname

        self.assertEqual(partner_form.firstname, False)
        self.assertEqual(partner_form.lastname, lastname)
        self.assertEqual(partner_form.name, lastname)

    def test_create_from_form_all(self):
        """A user creates a contact with all names from the form."""
        firstname = "Fïrst"
        lastname = "Läst"
        with Form(self.env["res.partner"]) as partner_form:
            self.set_company(partner_form)

            # Changes firstname, which triggers compute
            partner_form.firstname = firstname

            # Changes lastname, which triggers compute
            partner_form.lastname = lastname

        self.assertEqual(partner_form.lastname, lastname)
        self.assertEqual(partner_form.firstname, firstname)
        self.assertEqual(partner_form.name, f"{firstname} {lastname}")
