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
from textwrap import TextWrapper
from urllib import urlencode
from zope.cachedescriptors.property import Lazy
from gs.content.email.base import GroupEmail
from gs.group.base.page import GroupPage
from gs.profile.email.base.emailuser import EmailUser
UTF8 = 'utf-8'


def default_message(groupInfo):
    m = u'Please accept this invitation to join {0}. I am inviting you '\
        u'because...'
    return m.format(groupInfo.name)


def default_subject(groupInfo):
    return u'Invitation to join %s (Action required)' % groupInfo.name


class InvitationMessageMixin(object):
    @Lazy
    def supportEmail(self):
        sub = (u'Invitation to %s' % self.groupInfo.name).encode(UTF8)
        msg = (u'Hi!\n\nI received an invitation to join the group '
            u'%s\n    %s\nand...' % (self.groupInfo.name,
                self.groupInfo.url)).encode(UTF8)
        data = {
          'Subject': sub,
          'body': msg,
        }
        retval = 'mailto:%s?%s' % \
            (self.siteInfo.get_support_email(), urlencode(data))
        return retval

    def get_addr(self, userInfo):
        eu = EmailUser(self.context, userInfo)
        a = eu.get_verified_addresses()
        retval = (a and a[0]) or eu.get_addresses()[0]
        assert retval
        return retval

    def format_message(self, m):
        retval = FormattedMessage(m).html
        return retval

    @Lazy
    def defaultSubject(self):
        return default_subject(self.groupInfo)

    @Lazy
    def defaultMessage(self):
        retval = default_message(self.groupInfo)
        return retval.encode(UTF8)


class InvitationMessage(GroupEmail, InvitationMessageMixin):

    def __init__(self, context, request):
        super(InvitationMessage, self).__init__(context, request)


class InvitationMessageText(GroupPage, InvitationMessageMixin):
    def __init__(self, context, request):
        super(InvitationMessageText, self).__init__(context, request)
        response = request.response
        response.setHeader("Content-Type", 'text/plain; charset=UTF-8')
        filename = 'invitation-to-%s.txt' % self.groupInfo.name
        response.setHeader('Content-Disposition',
                            'inline; filename="%s"' % filename)

    def format_message(self, m):
        retval = FormattedMessage(m).txt.rstrip()
        return retval

    def format_message_no_indent(self, m):
        tw = TextWrapper()
        retval = tw.fill(m)
        return retval


class FormattedMessage(object):
    def __init__(self, message):
        self.originalMessage = message

    @Lazy
    def html(self):
        p = '<p style="margin: 1.385em 0 1.385em 1.385em;">'
        withPara = self.originalMessage.replace(u'\n\n', u'</p>%s' % p)
        withBr = withPara.replace('u\n', u'<br/>')
        retval = '%s%s</p>' % (p, withBr)
        return retval

    @Lazy
    def txt(self):
        tw = TextWrapper(initial_indent='    ',
                         subsequent_indent='    ')
        retval = ''
        for line in self.originalMessage.splitlines():
            p = tw.fill(line.strip())
            retval = '%s%s\n\n' % (retval, p)
        return retval
