# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy
from gs.group.member.viewlet import GroupAdminViewlet
from gs.site.member import SiteMembers
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
