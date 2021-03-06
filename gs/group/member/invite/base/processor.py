# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from __future__ import absolute_import, unicode_literals
from zope.formlib import form
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from Products.GSProfile.utils import create_user_from_email
from gs.content.form.base.utils import enforce_schema
from gs.profile.email.base import NewEmailAddress, EmailAddressExists, \
    sanitise_address
from gs.group.member.base import user_member_of_group
from .audit import Auditor, INVITE_NEW_USER, INVITE_OLD_USER, \
    INVITE_EXISTING_MEMBER
from .inviter import Inviter
from .utils import set_digest


class InviteProcessor(object):
    """The class that does the technical work of inviting a user based on
data provided by another user.

:param object context: Zope context object. Should be a Group context.
:param object request: Zope request that is causing this invitation.
:param siteInfo: SiteInfo object for the Site that a user is joining a
                 group in.
:type siteInfo: :class:`Products.GSContent.interfaces.IGSSiteInfo
:param groupInfo: GroupInfo object for the Group that a user is being
                  invited to.
:type groupInfo: :class:`Products.GSGroup.interfaces.IGSGroupInfo`
:param invitingUserInfo: UserInfo object representing the user who is doing
                         the inviting
:type invitingUserInfo:
        :class:`Products.CustomUserFolder.interfaces.IGSUserInfo`
:param form_fields: The fileds used by the form that is creating an
                    instance of :class:`InviteProcessor`
:type form_fields: :class:`zope.formlib.Fields`
:param inviteFields: InviteFields object that governs what data is
                     required to process the invite."""

    def __init__(self, context, request, siteInfo, groupInfo,
                 invitingUserInfo, form_fields, inviteFields):
        self.context = context
        self.request = request
        self.siteInfo = siteInfo
        self.groupInfo = groupInfo
        self.invitingUserInfo = invitingUserInfo
        self.form_fields = form_fields
        self.inviteFields = inviteFields

    def process(self, data):
        """Attempt to invite a user to join a group based on the provided
data.

:param dict data: The data submitted to the form, assumed to be data used
                  to invite a person to a group
:returns: If successful, a 2-tuple of ``(status_code, userInfo)``
          containing a status code indicating the result of processing the
          invite and an IGSUserInfo instance
:rtype: tuple"""
        userInfo = None

        acl_users = self.context.acl_users
        toAddr = sanitise_address(data['toAddr'])

        emailChecker = NewEmailAddress(title='Email')
        emailChecker.context = self.context

        try:
            emailChecker.validate(toAddr)  # Can handle a full address
        except EmailAddressExists:
            user = acl_users.get_userByEmail(toAddr)  # Cannot
            assert user, 'User for address <%s> not found' % toAddr
            userInfo = IGSUserInfo(user)
            auditor, inviter = self.get_auditor_inviter(userInfo)
            if user_member_of_group(user, self.groupInfo):
                auditor.info(INVITE_EXISTING_MEMBER, toAddr)
                status_code = INVITE_EXISTING_MEMBER
            else:
                inviteId = inviter.create_invitation(data, False)
                auditor.info(INVITE_OLD_USER, toAddr)
                # TODO: a DMARC lookup on the From. If there is DMARC on
                #       then construct a From from the support-email and the
                #       group-administrator's name
                inviter.send_notification(data['subject'],
                                          data['message'],
                                          inviteId,
                                          data['fromAddr'])  # No to-addr
                self.set_delivery(userInfo, data['delivery'])
                status_code = INVITE_OLD_USER
        else:
            # Email address does not exist, but it is a legitimate address
            user = create_user_from_email(self.context, toAddr)
            userInfo = IGSUserInfo(user)
            self.add_profile_attributes(userInfo, data)
            auditor, inviter = self.get_auditor_inviter(userInfo)
            inviteId = inviter.create_invitation(data, True)
            auditor.info(INVITE_NEW_USER, toAddr)
            inviter.send_notification(data['subject'], data['message'],
                                      inviteId, data['fromAddr'],
                                      toAddr)  # Note the to-addr
            self.set_delivery(userInfo, data['delivery'])
            status_code = INVITE_NEW_USER

        assert status_code
        assert user, 'User not created or found'
        return (status_code, userInfo)

    def add_profile_attributes(self, userInfo, data):
        enforce_schema(userInfo.user, self.inviteFields.profileInterface)
        fields = self.form_fields.select(*self.inviteFields.profileFieldIds)
        for field in fields:
            field.interface = self.inviteFields.profileInterface

        form.applyChanges(userInfo.user, fields, data)
        # wpb: Why not use self.set_delivery?
        set_digest(userInfo, self.groupInfo, data)

    def get_auditor_inviter(self, userInfo):
        """Retrives the Inviter and Auditor objects that will be used to
invite the user.

:param userInfo: The user who will be invited.
:type userInfo: :class:`Products.CustomUserFolder.interfaces.IGSUserInfo`
:returns: A 2-tuple ``(Auditor, Inviter)``
:rtype: tuple"""
        ctx = get_the_actual_instance_from_zope(self.context)
        inviter = Inviter(ctx, self.request, userInfo,
                          self.invitingUserInfo,
                          self.siteInfo, self.groupInfo)
        auditor = Auditor(self.siteInfo, self.groupInfo,
                          self.invitingUserInfo, userInfo)
        return (auditor, inviter)

    def set_delivery(self, userInfo, delivery):
        """Convenience method for setting the delivery method of a user in
a group.

:param userInfo: The user to set delivery for.
:type userInfo: :class:`Products.CustomUserFolder.interfaces.IGSUserInfo`
:param str delivery: The desired delivery setting. Allowed values are
                    ``email``, ``digest``, and ``web``."""
        if delivery == 'email':
            # --=mpj17=-- The default is one email per post
            pass
        elif delivery == 'digest':
            userInfo.user.set_enableDigestByKey(self.groupInfo.id)
        elif delivery == 'web':
            userInfo.user.set_disableDeliveryByKey(self.groupInfo.id)
