# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class CreateProjectInvoicePlanWizard(models.TransientModel):
    _name = 'project.invoice.plan.create.wizard'
    _description = 'Wizard cor creating Project invoice plan'

    date_from = fields.Date(
        string='Date From', required=True)
    date_to = fields.Date(
        string='Date To', required=True)
    invoice_date = fields.Date(
        string='Invoice Date', required=True)
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project', required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer", required=True
    )

    @api.multi
    def button_create_plan(self):
        timesheets = self.env['account.analytic.line']
        sql_params = {
            'date_from': datetime.strftime(self.date_from, DEFAULT_SERVER_DATE_FORMAT),
            'date_to': datetime.strftime(self.date_to, DEFAULT_SERVER_DATE_FORMAT),
            'project_id': self.project_id.id
        }

        check_employee_sql = """
        select max(e.timesheet_product_id) as product
             , max(e."name") as employee
        from account_analytic_line as aal
        join project_project pp on pp.id = aal.project_id
        join hr_employee e on e.id = aal.employee_id
        where aal.date >= %(date_from)s   --'2019-08-01'::date
          and aal.date <= %(date_to)s     --'2019-10-01'::date
          and pp.id = %(project_id)s      --21
          and e.timesheet_product_id is null
          and aal.project_invoice_plan_line_id is NULL
          and aal.unit_amount > 0.0
        group by e.id
        """
        self.env.cr.execute(check_employee_sql, sql_params)
        bad_employees = self.env.cr.dictfetchall()
        if bad_employees:
            msg = ', '.join([e['employee'] for e in bad_employees])
            raise UserError(_('Please add timesheet product on employees: ') + msg)

        product_sql = """
        
        DROP AGGREGATE IF EXISTS array_concat_agg(anyarray);
        CREATE AGGREGATE array_concat_agg(anyarray) (
          SFUNC = array_cat,
          STYPE = anyarray
        );
        
        WITH a AS 
        (
        select
                SUM(aal.unit_amount) as sub_amount
              , coalesce(aal.product_id, e.timesheet_product_id) as product_id
              , coalesce(pt.name, 'UNDEFINED') as task_name
              , array_agg(aal.id) as line_ids
              , pt.id as task_id
         from account_analytic_line as aal
         join project_project pp on pp.id = aal.project_id
         left join project_task pt on pt.id = aal.task_id 
         join hr_employee e on e.id = aal.employee_id

         where pp.id = %(project_id)s       -- 21
           and aal.date >= %(date_from)s    --'2019-08-01'::date
           and aal.date <= %(date_to)s      --'2019-10-01'::date
           and aal.project_invoice_plan_line_id is NULL
           and aal.unit_amount > 0.0
         group by coalesce(aal.product_id, e.timesheet_product_id), pt.id
        )
        
        select a.product_id
             , sum(a.sub_amount) amount
             , max(pt.name) product_name
             , max(pt.list_price) price
             , string_agg(a.task_name::varchar || ': ' ||a.sub_amount::varchar, '\n' order by a.task_id) as description
             , array_concat_agg(a.line_ids) as account_analytic_lines
        from a
        left join product_product pp on pp.id = a.product_id
        left join product_template pt on pt.id = pp.product_tmpl_id
        group by a.product_id
        """
        self.env.cr.execute(product_sql, sql_params)
        plan_lines = self.env.cr.dictfetchall()
        if not plan_lines:
            raise Warning(_('No data for invoicing'))

        invoice_plan_lines = []
        for line in plan_lines:
            vals = {
                'name': line['product_name'],
                'product_id': line['product_id'],
                'project_id': self.project_id.id,
                'price_unit': line['price'],
                'quantity': line['amount'],
                'partner_id': self.partner_id.id,
                'description': line['description'],
                'account_analytic_line_ids': [(4, line_id) for line_id in line['account_analytic_lines']],
            }
            invoice_plan_lines.append((0, 0, vals))

        plan_vals = {
            'name': 'Invoice plan for %s - %s' % (self.date_from, self.date_to),
            'invoice_date': self.invoice_date,
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': self.project_id.currency_id.id,
            'project_invoice_plan_line_ids': invoice_plan_lines
        }
        self.env['project.invoice.plan'].create(plan_vals)
        return True
