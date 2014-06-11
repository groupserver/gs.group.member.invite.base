# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals
from email.utils import parseaddr
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
#from Products.GSProfile.edit_profile import wym_editor_widget
from gs.content.form.base import select_widget, radio_widget
from gs.group.base import GroupForm
from gs.profile.email.base.emailuser import EmailUser
from .invitefields import InviteFields
from .notifymessages import default_message, default_subject
from .audit import INVITE_NEW_USER, INVITE_OLD_USER, INVITE_EXISTING_MEMBER
from .processor import InviteProcessor


class InviteEditProfileForm(GroupForm):
    label = 'Invite a New Group Member'
    # Why is abscompath needed?
    #pageTemplateFileName = abscompath(gs.group.member.invite.base,
    #                                'browser/templates/edit_profile_invite.pt')
    pageTemplateFileName = 'browser/templates/edit_profile_invite.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        super(InviteEditProfileForm, self).__init__(group, request)
        self.inviteFields = InviteFields(group)

    @Lazy
    def form_fields(self):
        retval = form.Fields(self.inviteFields.adminInterface,
                             render_context=False)
        retval['tz'].custom_widget = select_widget
        #retval['biography'].custom_widget = wym_editor_widget
        retval['delivery'].custom_widget = radio_widget
        return retval

    @Lazy
    def defaultFromEmail(self):
        emailUser = EmailUser(self.context, self.adminInfo)
        retval = emailUser.get_delivery_addresses()[0]
        return retval

    def setUpWidgets(self, ignore_request=False):
        data = {'fromAddr': self.defaultFromEmail}

        siteTz = self.siteInfo.get_property('tz', 'UTC')
        defaultTz = self.groupInfo.get_property('tz', siteTz)
        data['tz'] = defaultTz
        data['subject'] = default_subject(self.groupInfo)
        data['message'] = default_message(self.groupInfo)

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    @form.action(label='Invite', failure='handle_invite_action_failure')
    def handle_invite(self, action, data):
        inviteProcessor = InviteProcessor(self.context, self.request,
                                          self.siteInfo, self.groupInfo,
                                          self.loggedInUser, self.form_fields,
                                          self.inviteFields)
        result, userInfo = inviteProcessor.process(data)

        # Prep data for display
        addrName, addr = parseaddr(data['toAddr'].strip())
        e = '<code class="email">%s</code>' % addr
        g = groupInfo_to_anchor(self.groupInfo)
        u = userInfo_to_anchor(userInfo)

        if result == INVITE_NEW_USER:
            m = '<li>A profile for {0} has been created, and given the '\
                'email address {1}.</li>\n'\
                '<li>{0} has been sent an invitation to join {2}.</li>'
            self.status = m.format(u, e, g)

        elif result == INVITE_OLD_USER:
            m = '<li>Inviting the existing person with the email address '\
                '{0} &#8213; {1} &#8213; to join {2}.</li>'
            self.status = m.format(e, u, g)

        elif result == INVITE_EXISTING_MEMBER:
            m = '<li>The person with the email address {0} &#8213; {1} '\
                '&#8213; is already a member of {2}.</li>\n'\
                '<li>No changes to the profile of {1} have been made.</li>'
            self.status = m.format(e, u, g)

        else:
            # What happened?
            m = '<li>An unknown event occurred while attempting to invite '\
                'the person with the email address {0} &#8213; {1} '\
                '&#8213; is already a member of {2}.</li>\n'\
                '<li>No changes to the profile of {1} have been made.</li>'
            self.status = m.format(e, u, g)

        self.status = '<ul>\n{0}\n</ul>'.format(self.status)
        assert userInfo, 'User not created or found'
        assert self.status

    def handle_invite_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'

    # Non-Standard methods below this point
    @property
    def adminInfo(self):
        return self.loggedInUser

    @property
    def adminWidgets(self):
        return self.inviteFields.get_admin_widgets(self.widgets)

    @property
    def profileWidgets(self):
        return self.inviteFields.get_profile_widgets(self.widgets)

    @property
    def requiredProfileWidgets(self):
        widgets = self.inviteFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if widget.required]
        return widgets

    @property
    def optionalProfileWidgets(self):
        widgets = self.inviteFields.get_profile_widgets(self.widgets)
        widgets = [widget for widget in widgets if not(widget.required)]
        return widgets
