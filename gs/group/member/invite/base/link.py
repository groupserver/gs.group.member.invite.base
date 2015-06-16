# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013, 2015 OnlineGroups.net and Contributors.
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
from zope.cachedescriptors.property import Lazy
from gs.group.member.viewlet import GroupAdminViewlet
from gs.site.member.base import SiteMembers
from Products.GSGroupMember.groupmembership import GroupMembers


class LinkSiteMember(GroupAdminViewlet):

    def __init__(self, group, request, view, manager):
        super(LinkSiteMember, self).__init__(group, request, view, manager)

    @Lazy
    def siteMembers(self):
        retval = SiteMembers(self.context)
        return retval

    @Lazy
    def groupMembers(self):
        retval = GroupMembers(self.context)
        return retval

    @Lazy
    def show(self):
        isAdmin = super(LinkSiteMember, self).show
        peopleToInvite = len(self.siteMembers) > len(self.groupMembers)
        retval = isAdmin and peopleToInvite
        return retval
