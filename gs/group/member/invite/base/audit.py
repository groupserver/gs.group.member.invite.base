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
from __future__ import unicode_literals
from pytz import UTC
from datetime import datetime
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, \
    AuditQuery, event_id_from_data
SUBSYSTEM = 'gs.group.member.invite'
import logging
log = logging.getLogger(SUBSYSTEM)

UNKNOWN = '0'
INVITE_NEW_USER = '1'
INVITE_OLD_USER = '2'
INVITE_EXISTING_MEMBER = '3'
WITHDRAW_INVITATION = '4'

CSS_CLASS = 'audit-event profile-invite-event-{0}'
EMAIL = '<code class="email">{0}</code>'


class AuditEventFactory(object):
    implements(IFactory)
    title = 'User Profile Invitation Audit-Event Factory'
    description = 'Creates a GroupServer audit event for invitations'

    def __call__(self, context, event_id, code, date, userInfo,
                instanceUserInfo, siteInfo, groupInfo, instanceDatum='',
                supplementaryDatum='', subsystem=''):

        if (code == INVITE_NEW_USER):
            event = InviteNewUserEvent(context, event_id, date,
              userInfo, instanceUserInfo, siteInfo, groupInfo,
              instanceDatum, supplementaryDatum)
        elif (code == INVITE_OLD_USER):
            event = InviteOldUserEvent(context, event_id, date,
              userInfo, instanceUserInfo, siteInfo, groupInfo,
              instanceDatum, supplementaryDatum)
        elif (code == INVITE_EXISTING_MEMBER):
            event = InviteExistingMemberEvent(context, event_id, date,
              userInfo, instanceUserInfo, siteInfo, groupInfo,
              instanceDatum, supplementaryDatum)
        elif (code == WITHDRAW_INVITATION):
            event = WithdrawInvitationEvent(context, event_id, date,
              userInfo, instanceUserInfo, siteInfo, groupInfo)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
              userInfo, instanceUserInfo, siteInfo, groupInfo,
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


class InviteNewUserEvent(BasicAuditEvent):
    """Administrator inviting a New User Event.

    The "instanceDatum" is the address used to create the new user.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                siteInfo, groupInfo, instanceDatum, supplementaryDatum):

        BasicAuditEvent.__init__(self, context, id, INVITE_NEW_USER, d,
                                userInfo, instanceUserInfo, siteInfo, groupInfo,
                                instanceDatum, supplementaryDatum,
          SUBSYSTEM)

    def __unicode__(self):
        r = 'Administrator {0} ({1}) inviting a new user {2} ({3}) with '\
              'address <{4}> to join {5} ({6}) on {7} ({8})'
        retval = r.format(self.userInfo.name, self.userInfo.id,
                          self.instanceUserInfo.name, self.instanceUserInfo.id,
                          self.instanceDatum,
                          self.groupInfo.name, self.groupInfo.id,
                          self.siteInfo.name, self.siteInfo.id)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = CSS_CLASS.format(self.code)
        email = EMAIL.format(self.instanceDatum)
        ua = userInfo_to_anchor(self.instanceUserInfo)
        ga = groupInfo_to_anchor(self.groupInfo)
        r = '<span class="{0}">Invited the new user {1} (with the '\
            'email address {2}) to join {3}.</span>'
        retval = r.format(cssClass, ua, email, ga)
        if ((self.instanceUserInfo.id != self.userInfo.id)
            and not(self.userInfo.anonymous)):
            retval = '%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        return retval


class InviteOldUserEvent(BasicAuditEvent):
    """Administrator Inviting an old User Event.

    The "instanceDatum" is the address used to match the old user.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                    siteInfo, groupInfo, instanceDatum, supplementaryDatum):

        BasicAuditEvent.__init__(self, context, id,
          INVITE_OLD_USER, d, userInfo, instanceUserInfo,
          siteInfo, groupInfo, instanceDatum, supplementaryDatum,
          SUBSYSTEM)

    def __unicode__(self):
        r = 'Administrator {0} ({1}) inviting an existing user {2} ({3}) '\
            'with address <{4}> to join {5} ({6}) on {7} ({8})'
        retval = r.format(self.userInfo.name, self.userInfo.id,
                          self.instanceUserInfo.name, self.instanceUserInfo.id,
                          self.instanceDatum,
                          self.groupInfo.name, self.groupInfo.id,
                          self.siteInfo.name, self.siteInfo.id)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = CSS_CLASS.format(self.code)
        email = EMAIL.format(self.instanceDatum)
        ua = userInfo_to_anchor(self.instanceUserInfo)
        ga = groupInfo_to_anchor(self.groupInfo)
        r = '<span class="{0}">Invited the existing user {1} (with the '\
            'email address {2}) to join {3}.</span>'
        retval = r.format(cssClass, ua, email, ga)
        if ((self.instanceUserInfo.id != self.userInfo.id)
            and not(self.userInfo.anonymous)):
            retval = '%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        return retval


class InviteExistingMemberEvent(BasicAuditEvent):
    """Administrator Inviting an Existing Group Member.

    The "instanceDatum" is the address used to match the existing group
    member.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
                    siteInfo, groupInfo, instanceDatum, supplementaryDatum):

        BasicAuditEvent.__init__(self, context, id,
          INVITE_OLD_USER, d, userInfo, instanceUserInfo,
          siteInfo, groupInfo, instanceDatum, supplementaryDatum,
          SUBSYSTEM)

    def __unicode__(self):
        r = 'Administrator {0} ({1}) tried to invite an existing group '\
              'member {2} ({3}) with address <{4}> to join {5} ({6}) on {7} '\
              '({8})'
        retval = r.format(self.userInfo.name, self.userInfo.id,
                          self.instanceUserInfo.name, self.instanceUserInfo.id,
                          self.instanceDatum,
                          self.groupInfo.name, self.groupInfo.id,
                          self.siteInfo.name, self.siteInfo.id)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = CSS_CLASS.format(self.code)
        email = EMAIL.format(self.instanceDatum)
        ua = userInfo_to_anchor(self.instanceUserInfo)
        ga = groupInfo_to_anchor(self.groupInfo)
        r = '<span class="{0}">Tried to invite the existing member '\
            ' {1} (with email {2}) to join {3}.</span>'
        retval = r.format(cssClass, ua, email, ga)
        if ((self.instanceUserInfo.id != self.userInfo.id)
            and not(self.userInfo.anonymous)):
            retval = '%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        return retval


class WithdrawInvitationEvent(BasicAuditEvent):
    """Administrator Withdrawing an Invitation

        Invitations are withdrawn based on userID, so there is
        no instanceDatum or supplementaryDatum required here.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
        siteInfo, groupInfo):

        BasicAuditEvent.__init__(self, context, id,
          WITHDRAW_INVITATION, d, userInfo, instanceUserInfo,
          siteInfo, groupInfo, None, None, SUBSYSTEM)

    def __unicode__(self):
        r = 'Administrator {0} ({1}) withdrew the invitation to {2} ({3}) '\
            'to join {4} ({5}) on {6} ({7})'
        retval = r.format(self.userInfo.name, self.userInfo.id,
                        self.instanceUserInfo.name, self.instanceUserInfo.id,
                        self.groupInfo.name, self.groupInfo.id,
                        self.siteInfo.name, self.siteInfo.id)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event profile-invite-event-%s' % self.code
        retval = '<span class="%s">Withdrew the invitation to '\
            'join %s from %s.</span>' %\
            (cssClass, groupInfo_to_anchor(self.groupInfo),
             userInfo_to_anchor(self.instanceUserInfo))
        if ((self.instanceUserInfo.id != self.userInfo.id)
            and not(self.userInfo.anonymous)):
            retval = '%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        return retval


class Auditor(object):
    def __init__(self, siteInfo, groupInfo, adminInfo, userInfo):
        self.siteInfo = siteInfo
        self.groupInfo = groupInfo
        self.adminInfo = adminInfo
        self.userInfo = userInfo

        self.queries = AuditQuery()

        self.factory = AuditEventFactory()

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        d = datetime.now(UTC)
        eventId = event_id_from_data(self.adminInfo, self.userInfo,
            self.siteInfo, code, instanceDatum, supplementaryDatum)

        e = self.factory(self.userInfo.user, eventId, code, d, self.adminInfo,
                        self.userInfo, self.siteInfo, self.groupInfo,
                        instanceDatum, supplementaryDatum, SUBSYSTEM)
        self.queries.store(e)
        log.info(e)
