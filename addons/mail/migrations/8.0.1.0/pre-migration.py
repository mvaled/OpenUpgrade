# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Akretion (http://www.akretion.com/)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#    (<http://www.savoirfairelinux.com>).
#    @author: Onestein <www.onestein.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade

column_renames = {
    'res_partner': [
        ('notification_email_send', None),
    ],
    'mail_mail': [
        ('email_from', None),
        ('mail_server_id', None),
        ('reply_to', None),
    ]
}


def ensure_single_followers(cr):
    # Before certain point in OpenERP 7.0 the mail_followers table allowed a
    # partner to follow the same topic several times::
    #
    #    IntegrityError: could not create unique index "mail_followers_mail_followers_res_partner_res_model_id_uniq"
    #    DETAIL:  Key (res_model, res_id, partner_id)=(crm.lead, 1459, 417) is duplicated.
    #
    # This error avoids the creation of the unique index.
    #
    # This migration step finds any duplicated rows and leaves a single one.
    cr.execute('''
       SELECT res_model, res_id, partner_id, many
       FROM (SELECT res_model, res_id, partner_id, COUNT(id) as many
             FROM mail_followers
             GROUP BY res_model, res_id, partner_id) AS multi_follower
       WHERE many > 1
    ''')
    for res_model, res_id, partner_id, _ in cr.fetchall():
        cr.execute('''
           DELETE FROM mail_followers
              WHERE res_model=%s AND res_id=%s AND partner_id=%s;

           INSERT INTO mail_followers (res_model, res_id, partner_id)
              VALUES (%s, %s, %s);
        ''', (res_model, res_id, partner_id) * 2)


@openupgrade.migrate()
def migrate(cr, version):
    ensure_single_followers(cr)
    openupgrade.rename_columns(cr, column_renames)
