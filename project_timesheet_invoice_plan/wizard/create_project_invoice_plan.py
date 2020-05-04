# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT




class CreateProjectInvoicePlanWizard(models.TransientModel):
    _name = 'project.invoice.plan.create.wizard'
    _description = 'Wiizard cor creating Project invoice plan'

    date_from = fields.Date(
        string='Date From', required=True)
    date_to = fields.Date(
        string='Date To', required=True)
    invoice_date = fields.Date(
        string='Invoice Date', required=True)
    name = fields.Char(string='Name')
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
        group by e.id
        """
        self.env.cr.execute(check_employee_sql, sql_params)
        bad_employees = self.env.cr.dictfetchall()
        if bad_employees:
            msg = ', '.join([e['employee'] for e in bad_employees])
            raise UserError(_('Please add timesheet product on employees: ') + msg)

        product_sql = """
        select a.product_id
             , sum(a.unit_amount) amount
             , max(pt.name) product_name
             , max(pt.list_price) price
        from (	
	         select aal.id 
	              , aal.date
	              , aal.unit_amount 
	              , coalesce(aal.product_id, e.timesheet_product_id) as product_id
	              , e."name" 
	         from account_analytic_line as aal
	         join project_project pp on pp.id = aal.project_id 
	         join hr_employee e on e.id = aal.employee_id 
	
	         where pp.id = %(project_id)s       -- 21
	           and aal.date >= %(date_from)s    --'2019-08-01'::date
	           and aal.date <= %(date_to)s      --'2019-10-01'::date
	         ) a
	    left join product_product pp on pp.id = a.product_id
        left join product_template pt on pt.id = pp.product_tmpl_id      
        group by a.product_id
        """
        self.env.cr.execute(product_sql, sql_params)
        plan_items = self.env.cr.dictfetchall()
        if not plan_items:
            raise Warning(_('No data for invoicing'))

        invoice_plan_items = []
        for item in plan_items:
            vals = {
                'product_id': item['product_id'],
                'project_id': self.project_id.id,
                'price_unit': item['price'],
                'quantity': item['amount'],
                'partner_id': self.partner_id.id
            }
            invoice_plan_items.append((0, 0, vals))


        plan_vals = {
            'name': 'Invoice plan for %s - %s' % (self.date_from, self.date_to),
            'invoice_date': self.invoice_date,
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'invoice_plan_item_ids': invoice_plan_items
        }
        self.env['project.invoice.plan'].create(plan_vals)





        return True
