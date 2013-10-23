# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from gs.content.form import radio_widget, multi_check_box_widget
from gs.profile.email.base.emailuser import EmailUser
from gs.group.base import GroupForm
from .interfaces import IGSInviteSiteMembers
from .notifymessages import default_message, default_subject
from .inviter import Inviter
from .audit import Auditor, INVITE_OLD_USER


class GSInviteSiteMembersForm(GroupForm):
    label = u'Invite Site Members'
    pageTemplateFileName = 'browser/templates/invitesitemembers.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        super(GSInviteSiteMembersForm, self).__init__(context, request)

    @Lazy
    def form_fields(self):
        retval = form.Fields(IGSInviteSiteMembers, render_context=False)
        retval['site_members'].custom_widget = multi_check_box_widget
        retval['delivery'].custom_widget = radio_widget
        return retval

    @property
    def adminInfo(self):
        return self.loggedInUser

    @property
    def defaultFromEmail(self):
        emailUser = EmailUser(self.context, self.adminInfo)
        retval = emailUser.get_delivery_addresses()[0]
        return retval

    def setUpWidgets(self, ignore_request=False):
        data = {'fromAddr': self.defaultFromEmail,
                'delivery': 'email'}
        data['subject'] = default_subject(self.groupInfo)
        data['message'] = default_message(self.groupInfo)

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    @form.action(label=u'Invite', failure='handle_invite_action_failure')
    def handle_invite(self, action, data):
        for userId in data['site_members']:
            ctx = get_the_actual_instance_from_zope(self.context)
            userInfo = createObject('groupserver.UserFromId', ctx,
                                        userId)
            inviter = Inviter(ctx, self.request, userInfo,
                        self.adminInfo, self.siteInfo, self.groupInfo)
            inviteId = inviter.create_invitation(data, False)
            auditor = Auditor(self.siteInfo, self.groupInfo,
                        self.adminInfo, userInfo)
            auditor.info(INVITE_OLD_USER)
            inviter.send_notification(data['subject'], data['message'],
                                        inviteId, data['fromAddr'])

            s = '{0}\n<li><a href="{1}">{2}</a></li>\n'
            self.status = s.format(self.status, userInfo.url, userInfo.name)
            self.set_delivery(userInfo, data['delivery'])

        self.status = u'<p>Invited the following users to '\
          u'join <a class="fn" href="%s">%s</a></p><ul>%s</ul>' %\
            (self.groupInfo.relativeURL, self.groupInfo.name, self.status)

        if not(data['site_members']):
            self.status = u'<p>No site members were selected.</p>'
        assert self.status
        assert type(self.status) == unicode

    def handle_invite_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_delivery(self, userInfo, delivery):
        if delivery == 'email':
            # --=mpj17=-- The default is one email per post
            pass
        elif delivery == 'digest':
            userInfo.user.set_enableDigestByKey(self.groupInfo.id)
        elif delivery == 'web':
            userInfo.user.set_disableDeliveryByKey(self.groupInfo.id)
