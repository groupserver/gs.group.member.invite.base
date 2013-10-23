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
from zope.component import createObject, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from gs.profile.notify.sender import MessageSender
UTF8 = 'utf-8'


class InvitationNotifier(object):
    textTemplateName = 'invitationmessage.txt'
    htmlTemplateName = 'invitationmessage.html'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.oldContentType = self.request.response.getHeader('Content-Type')

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.context)
        assert retval, 'Could not create the GroupInfo from %s' % self.context
        return retval

    @Lazy
    def loggedInUserInfo(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        assert retval, 'Could not create the user-info for the logged '\
            'in user from %s' % self.context
        return retval

    @Lazy
    def textTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                    name=self.textTemplateName)
        assert retval
        return retval

    @Lazy
    def htmlTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                    name=self.htmlTemplateName)
        assert retval
        return retval

    def notify(self, adminInfo, userInfo, fromAddr, toAddrs,
                invitationId, subject, message):
        assert toAddrs, 'No to address for %s' % userInfo.name
        text = self.textTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                    fromAddr=fromAddr, toAddr=toAddrs[0],
                                    subject=subject, invitationId=invitationId,
                                    message=message, fakeHeader=False)
        html = self.htmlTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                    fromAddr=fromAddr, toAddr=toAddrs[0],
                                    subject=subject, invitationId=invitationId,
                                    message=message, fakeHeader=False)
        html = ''  # FIXME
        ms = MessageSender(self.context, userInfo)
        ms.send_message(subject, text, html, fromAddr, toAddrs)
        self.request.response.setHeader('Content-Type', self.oldContentType)
