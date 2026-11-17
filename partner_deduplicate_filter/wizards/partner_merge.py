# Copyright 2016 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import SQL


class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = "base.partner.merge.automatic.wizard"

    exclude_is_company = fields.Boolean("'Is a company?' field selected")
    exclude_not_parent = fields.Boolean("Parent company not set")
    exclude_parent = fields.Boolean("Parent company set (Contacts)")

    def _get_exclusion_conditions(self):
        filters = []
        if self.exclude_is_company:
            filters.append("is_company = False")
        if self.exclude_not_parent:
            filters.append("parent_id IS NOT NULL")
        if self.exclude_parent:
            filters.append("parent_id IS NULL")
        return filters

    def _process_query(self, query):
        filters = self._get_exclusion_conditions()
        # Odoo 20 builds the query as an SQL object; the conditions have to be
        # injected before its GROUP BY, keeping the parameters untouched.
        if filters and isinstance(query, SQL):
            code, params, to_flush = query._sql_tuple
            index_group_by = code.rfind("GROUP BY")
            if index_group_by > 0:
                subquery = " AND ".join(filters)
                if "WHERE" in code[:index_group_by]:
                    subquery = f"AND ({subquery}) "
                else:  # pragma: no cover
                    subquery = f"WHERE {subquery} "
                code = (
                    code[:index_group_by]
                    + subquery
                    + code[index_group_by:]
                )
                query = SQL(code, *params, to_flush=to_flush)
        return super()._process_query(query)
