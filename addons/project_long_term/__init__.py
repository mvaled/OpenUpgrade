from openerp.osv.orm import Model, TransientModel


class phase(Model):
    _name = 'project.phase'


class project_user_allocation(Model):
    _name = 'project.user.allocation'


class project_compute_phases(TransientModel):
    _name = 'project.compute.phases'


class project_compute_tasks(TransientModel):
    _name = 'project.compute.tasks'
