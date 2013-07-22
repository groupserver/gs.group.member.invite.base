# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSGroupMember.groupMembersInfo import GSGroupMembersInfo
from gs.group.base import GroupForm
from gs.profile.email.base.emailuser import EmailUser
from inviter import Inviter
from audit import Auditor, INVITE_OLD_USER, INVITE_EXISTING_MEMBER
from interfaces import IGSResendInvitation


class ResendInvitationForm(GroupForm):
    pageTemplateFileName = 'browser/templates/resend_invite.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        super(ResendInvitationForm, self).__init__(group, request)

        if 'form.userId' not in self.request.form:
            raise ValueError('No userId')
        self.userId = self.request.form['form.userId']

    @Lazy
    def label(self):
        retval = u'Resend the invitation to {0}'.format(self.userInfo.name)
        return retval

    @Lazy
    def form_fields(self):
        retval = form.Fields(IGSResendInvitation, render_context=False)
        return retval

    @Lazy
    def defaultFromEmail(self):
        emailUser = EmailUser(self.context, self.adminInfo)
        addrs = emailUser.get_delivery_addresses()
        retval = addrs and addrs[0] or ''
        return retval

    @Lazy
    def defaultToEmail(self):
        emailUser = EmailUser(self.context, self.userInfo)
        addrs = emailUser.get_addresses()
        retval = addrs and addrs[0] or ''
        return retval

    def setUpWidgets(self, ignore_request=False):
        data = {'fromAddr': self.defaultFromEmail,
                  'toAddr': self.defaultToEmail,
                  'userId': self.userId}
        subject = u'Another Invitation to Join {0} (Action Required)'
        data['subject'] = subject.format(self.groupInfo.name)

        m = u'''Hello {0}

Please accept this invitation to join {1}. I have set up a profile for you,
so you can start  participating in the group as soon as you accept this
invitation.'''

        data['message'] = m.format(self.userInfo.name, self.groupInfo.name)

        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)

    @form.action(label=u'Resend', failure='handle_invite_action_failure')
    def handle_invite(self, action, data):
        self.actual_handle_add(action, data)

    def handle_invite_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @Lazy
    def userInfo(self):
        retval = createObject('groupserver.UserFromId', self.context,
                            self.userId)
        return retval

    @Lazy
    def adminInfo(self):
        return self.loggedInUser

    def already_a_member(self, u, e, g):
        msg = u'<ul><li>{0} (with the email address {1}) is already a member '\
              u'of {2}.</li>\n<li>No changes have been made.</li></ul>'
        retval = msg.format(u, e, g)
        return retval

    def resent(self, u, e, g):
        msg = u'<ul><li>Resent an invitation to {0} (with the email '\
              u'address {1}) to join {2}.</li></ul>'
        retval = msg.format(u, e, g)
        return retval

    def issues(self, u, e, g):
        msg = u'<ul><li>Cannot <strong>resend</strong> an invitation to {0}, '\
              u'because he or she is yet been invited to join {1}.</li>'\
              u'<li>No changes have been made.</li>'
        retval = msg.format(u, g)
        return retval

    def actual_handle_add(self, action, data):
        e = u'<code class="email">%s</code>' % self.defaultToEmail
        u = userInfo_to_anchor(self.userInfo)
        g = groupInfo_to_anchor(self.groupInfo)
        auditor, inviter = self.get_auditor_inviter()
        membersInfo = GSGroupMembersInfo(self.groupInfo.groupObj)
        if self.userId in [m.id for m in membersInfo.fullMembers]:
            auditor.info(INVITE_EXISTING_MEMBER, self.defaultToEmail)
            self.status = self.already_a_member(u, e, g)
        elif self.userId in [m.id for m in membersInfo.invitedMembers]:
            self.status = self.resent(u, e, g)
            inviteId = inviter.create_invitation(data, False)
            auditor.info(INVITE_OLD_USER, self.defaultToEmail)
            inviter.send_notification(data['subject'], data['message'],
                                    inviteId, data['fromAddr'], data['toAddr'])
        else:
            self.status = self.issues(u, e, g)
        assert self.status

    def handle_add_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def get_auditor_inviter(self):
        ctx = get_the_actual_instance_from_zope(self.context)
        inviter = Inviter(ctx, self.request, self.userInfo,
                            self.adminInfo, self.siteInfo,
                            self.groupInfo)
        auditor = Auditor(self.siteInfo, self.groupInfo,
                    self.adminInfo, self.userInfo)
        return (auditor, inviter)
