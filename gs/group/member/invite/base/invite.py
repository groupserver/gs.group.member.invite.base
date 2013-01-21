# coding=utf-8
'''The form that allows an admin to invite a new person to join a group.'''
from email.utils import parseaddr
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope,\
    abscompath
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSProfile.edit_profile import select_widget, wym_editor_widget
from Products.GSProfile.utils import create_user_from_email, \
    enforce_schema
from gs.group.member.base.utils import user_member_of_group
from gs.group.base.form import GroupForm
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    EmailAddressExists
from gs.profile.email.base.emailuser import EmailUser
from gs.content.form.radio import radio_widget
from utils import set_digest
from invitefields import InviteFields
from inviter import Inviter
from notifymessages import default_message, default_subject
from audit import Auditor, INVITE_NEW_USER, INVITE_OLD_USER,\
    INVITE_EXISTING_MEMBER
import gs.group.member.invite.base  # For the abscompath call below


class InviteEditProfileForm(GroupForm):
    label = u'Invite a New Group Member'
    pageTemplateFileName = abscompath(gs.group.member.invite.base,
                                    'browser/templates/edit_profile_invite.pt')
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        GroupForm.__init__(self, group, request)
        self.inviteFields = InviteFields(group)

    @Lazy
    def form_fields(self):
        retval = form.Fields(self.inviteFields.adminInterface,
                    render_context=False)
        retval['tz'].custom_widget = select_widget
        retval['biography'].custom_widget = wym_editor_widget
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

    @form.action(label=u'Invite', failure='handle_invite_action_failure')
    def handle_invite(self, action, data):
        self.actual_handle_add(action, data)

    def handle_invite_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

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

    def actual_handle_add(self, action, data):
        userInfo = None

        acl_users = self.context.acl_users
        toAddr = data['toAddr'].strip()
        addrName, addr = parseaddr(toAddr)

        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context
        e = u'<code class="email">%s</code>' % addr
        g = groupInfo_to_anchor(self.groupInfo)

        try:
            emailChecker.validate(toAddr)  # Can handle a full address
        except EmailAddressExists:
            user = acl_users.get_userByEmail(addr)  # Cannot
            assert user, 'User for address <%s> not found' % addr
            userInfo = IGSUserInfo(user)
            u = userInfo_to_anchor(userInfo)
            auditor, inviter = self.get_auditor_inviter(userInfo)
            if user_member_of_group(user, self.groupInfo):
                auditor.info(INVITE_EXISTING_MEMBER, addr)
                self.status = u'''<li>The person with the email address %s
&#8213; %s &#8213; is already a member of %s.</li>''' % (e, u, g)
                self.status = u'%s<li>No changes to the profile of '\
                  '%s have been made.</li>' % (self.status, u)
            else:
                self.status = u'<li>Inviting the existing person with '\
                  u'the email address %s &#8213; %s &#8213; to join '\
                  u'%s.</li>' % (e, u, g)
                inviteId = inviter.create_invitation(data, False)
                auditor.info(INVITE_OLD_USER, addr)
                inviter.send_notification(data['subject'],
                    data['message'], inviteId, data['fromAddr'])  # No to-addr
                self.set_delivery(userInfo, data['delivery'])
        else:
            # Email address does not exist, but it is a legitimate address
            user = create_user_from_email(self.context, toAddr)
            userInfo = IGSUserInfo(user)
            self.add_profile_attributes(userInfo, data)
            auditor, inviter = self.get_auditor_inviter(userInfo)
            inviteId = inviter.create_invitation(data, True)
            auditor.info(INVITE_NEW_USER, addr)
            inviter.send_notification(data['subject'], data['message'],
                inviteId, data['fromAddr'], addr)  # Note the to-addr
            self.set_delivery(userInfo, data['delivery'])
            u = userInfo_to_anchor(userInfo)
            self.status = u'''<li>A profile for %s has been created, and
given the email address %s.</li>\n''' % (u, e)
            self.status = u'%s<li>%s has been sent an invitation to '\
              u'join %s.</li>\n' % (self.status, u, g)
        assert user, 'User not created or found'
        assert self.status
        return userInfo

    def add_profile_attributes(self, userInfo, data):
        enforce_schema(userInfo.user, self.inviteFields.profileInterface)
        fields = self.form_fields.select(*self.inviteFields.profileFieldIds)
        for field in fields:
            field.interface = self.inviteFields.profileInterface

        form.applyChanges(userInfo.user, fields, data)
        set_digest(userInfo, self.groupInfo, data)

    def get_auditor_inviter(self, userInfo):
        ctx = get_the_actual_instance_from_zope(self.context)
        inviter = Inviter(ctx, self.request, userInfo,
                            self.adminInfo, self.siteInfo,
                            self.groupInfo)
        auditor = Auditor(self.siteInfo, self.groupInfo,
                    self.adminInfo, userInfo)
        return (auditor, inviter)

    def set_delivery(self, userInfo, delivery):
        if delivery == 'email':
            # --=mpj17=-- The default is one email per post
            pass
        elif delivery == 'digest':
            userInfo.user.set_enableDigestByKey(self.groupInfo.id)
        elif delivery == 'web':
            userInfo.user.set_disableDeliveryByKey(self.groupInfo.id)
