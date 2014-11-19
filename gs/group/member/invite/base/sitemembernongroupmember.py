# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
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
from zope.cachedescriptors.property import Lazy
from zope.interface import implements, providedBy
from zope.component import createObject
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized, \
    ITitledTokenizedTerm
from zope.interface.common.mapping import IEnumerableMapping
from gs.group.member.base import user_member_of_group
from gs.profile.email.base.emailuser import EmailUser
from gs.site.member import SiteMembers


class SiteMembersNonGroupMembers(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context

    @Lazy
    def acl_users(self):
        sr = self.context.site_root()
        retval = sr.acl_users
        assert retval, 'No ACL Users'
        return retval

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.context)
        return retval

    @Lazy
    def groupsInfo(self):
        retval = createObject('groupserver.GroupsInfo', self.context)
        return retval

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.context)
        return retval

    @Lazy
    def siteMembers(self):
        return SiteMembers(self.context)

    def has_addr(self, ui):
        return bool(EmailUser(self.context, ui).get_delivery_addresses())

    @Lazy
    def nonMembers(self):
        '''Get the members of the current site that are not a member of
        the group, and who have an email address.'''
        # OPTIMIZE: This could *mostly* be done with lists of IDs
        retval = [EmailUser(self.context, ui)
                  for ui in self.siteMembers.members
                  if ((not user_member_of_group(ui, self.groupInfo))
                      and self.has_addr(ui))]
        assert type(retval) == list
        return retval

    @Lazy
    def nonMemberIds(self):
        retval = [m.userInfo.id for m in self.nonMembers]
        return retval

    def get_display_name(self, emailUser):
        userInfo = emailUser.userInfo
        addr = emailUser.get_delivery_addresses()[0]
        r = '{0} (<code class="email">{1}</code>)'
        retval = r.format(userInfo.name, addr)
        return retval

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        for m in self.nonMembers:
            uid = m.userInfo.id
            term = SimpleTerm(uid, uid, self.get_display_name(m))
            assert term
            assert ITitledTokenizedTerm in providedBy(term)
            assert term.token == term.value
            yield(term)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.nonMembers)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = value in self.nonMemberIds
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return self.getTermByToken(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        for m in self.nonMembers:
            uid = m.userInfo.id
            if uid == token:
                retval = SimpleTerm(uid, uid, self.get_display_name(m))
                assert retval
                assert ITitledTokenizedTerm in providedBy(retval)
                assert retval.token == retval.value
                return retval
        raise LookupError(token)
