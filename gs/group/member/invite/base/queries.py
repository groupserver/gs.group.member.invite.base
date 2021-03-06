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
from datetime import datetime
import pytz
import sqlalchemy as sa
from zope.sqlalchemy import mark_changed
from gs.database import getTable, getSession


class InvitationQuery(object):
    def __init__(self):
        self.userInvitationTable = getTable('user_group_member_invitation')

    def add_invitation(self, invitiationId, siteId, groupId, userId,
                       invtUsrId, initialInvite=False):
        assert invitiationId, 'invitiationId is %s' % invitiationId
        assert siteId, 'siteId is %s' % siteId
        assert groupId, 'groupId is %s' % groupId
        assert userId, 'userId is %s' % userId
        assert invtUsrId, 'invtUsrId is %s' % invtUsrId

        d = datetime.utcnow().replace(tzinfo=pytz.utc)
        i = self.userInvitationTable.insert()
        session = getSession()
        session.execute(i, params={'invitation_id': invitiationId,
                                   'site_id': siteId,
                                   'group_id': groupId,
                                   'user_id': userId,
                                   'inviting_user_id': invtUsrId,
                                   'invitation_date': d,
                                   'initial_invite': initialInvite})
        mark_changed(session)

    def marshal_invite(self, x):
        retval = {
            'invitation_id': x['invitation_id'],
            'user_id': x['user_id'],
            'inviting_user_id': x['inviting_user_id'],
            'site_id': x['site_id'],
            'group_id': x['group_id'],
            'invitation_date': x['invitation_date'],
            'response_date': x['response_date'],
            'accepted': x['accepted'],
            'initial_invite': x['initial_invite'],
            'withdrawn_date': x['withdrawn_date'],
            'withdrawing_user_id': x['withdrawing_user_id']}
        return retval

    def get_blank_invite(self):
        retval = {'invitation_id': '', 'user_id': '',
            'inviting_user_id': '', 'site_id': '', 'group_id': '',
            'invitation_date': '', 'response_date': '', 'accepted': ''}
        return retval

    def get_invitation(self, invitationId, current=True):
        uit = self.userInvitationTable
        s = uit.select()
        s.append_whereclause(uit.c.invitation_id == invitationId)
        if current:
            s.append_whereclause(uit.c.response_date == None)  # lint:ok
        session = getSession()
        r = session.execute(s)

        if r.rowcount:
            x = r.fetchone()
            retval = self.marshal_invite(x)
        else:
            retval = self.get_blank_invite()
        return retval

    def get_current_invitiations_for_site(self, siteId, userId):
        assert siteId
        assert userId
        uit = self.userInvitationTable
        s = uit.select(order_by=sa.desc(uit.c.invitation_date))
        s.append_whereclause(uit.c.site_id == siteId)
        s.append_whereclause(uit.c.user_id == userId)
        s.append_whereclause(uit.c.response_date == None)  # lint:ok
        s.append_whereclause(uit.c.withdrawn_date == None)  # lint:ok

        session = getSession()
        r = session.execute(s)

        seen = []
        retval = []
        if r.rowcount:
            for x in r:
                key = '%(site_id)s/%(group_id)s' % x
                if key not in seen:
                    seen.append(key)
                    retval.append(self.marshal_invite(x))
        assert type(retval) == list
        return retval

    def get_past_invitiations_for_site(self, siteId, userId):
        assert siteId
        assert userId
        uit = self.userInvitationTable
        cols = [uit.c.site_id, uit.c.group_id, uit.c.user_id,
                uit.c.inviting_user_id, uit.c.invitation_date,
                uit.c.response_date, uit.c.accepted]
        s = sa.select(cols, distinct=True,
                            order_by=sa.desc(uit.c.invitation_date))
        s.append_whereclause(uit.c.site_id == siteId)
        s.append_whereclause(uit.c.user_id == userId)
        s.append_whereclause(uit.c.response_date != None)  # lint:ok

        session = getSession()
        r = session.execute(s)

        retval = []
        if r.rowcount:
            retval = [self.marshal_invite(x) for x in r]
        assert type(retval) == list
        return retval

    def get_invitations_sent_by_user(self, siteId, invitingUserId):
        assert siteId
        assert invitingUserId
        uit = self.userInvitationTable
        cols = [uit.c.site_id, uit.c.group_id, uit.c.user_id,
                uit.c.invitation_date, uit.c.response_date, uit.c.accepted]
        s = sa.select(cols, distinct=True,
                            order_by=sa.desc(uit.c.invitation_date))
        s.append_whereclause(uit.c.site_id == siteId)
        s.append_whereclause(uit.c.inviting_user_id == invitingUserId)

        session = getSession()
        r = session.execute(s)

        retval = []
        if r.rowcount:
            retval = [self.marshal_invite(x) for x in r]
        assert type(retval) == list
        return retval

    def get_only_invitation(self, userInfo):
        it = self.userInvitationTable
        s = it.select()
        s.append_whereclause(it.c.response_date == None)  # lint:ok
        s.append_whereclause(it.c.withdrawn_date == None)  # lint:ok
        s.append_whereclause(it.c.user_id == userInfo.id )

        session = getSession()
        r = session.execute(s)

        assert r.rowcount < 2
        if r.rowcount:
            x = r.fetchone()
            retval = self.marshal_invite(x)
        else:
            retval = self.get_blank_invite()
        return retval

    def accept_invitation(self, siteId, groupId, userId):
        self.alter_invitation(siteId, groupId, userId, True)

    def decline_invitation(self, siteId, groupId, userId):
        self.alter_invitation(siteId, groupId, userId, False)

    def alter_invitation(self, siteId, groupId, userId, status):
        assert siteId
        assert groupId
        assert userId
        assert type(status) == bool

        d = datetime.utcnow().replace(tzinfo=pytz.utc)
        uit = self.userInvitationTable
        c = sa.and_(uit.c.site_id == siteId, uit.c.group_id == groupId,
                    uit.c.user_id == userId)
        v = {uit.c.response_date: d, uit.c.accepted: status}
        u = uit.update(c, values=v)

        session = getSession()
        session.execute(u)

        mark_changed(session)

    def withdraw_invitation(self, siteId, groupId, userId, withdrawingId):
        assert siteId
        assert groupId
        assert userId
        assert withdrawingId

        d = datetime.utcnow().replace(tzinfo=pytz.utc)
        uit = self.userInvitationTable
        c = sa.and_(uit.c.site_id == siteId, uit.c.group_id == groupId,
                    uit.c.user_id  == userId, uit.c.response_date == None,
                    uit.c.withdrawn_date == None)
        v = {uit.c.withdrawn_date: d, uit.c.withdrawing_user_id: withdrawingId}
        u = uit.update(c, values=v)

        session = getSession()
        session.execute(u)

        mark_changed(session)
