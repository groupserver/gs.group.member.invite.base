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
from gs.content.email.base import GroupEmail, TextMixin
from gs.profile.email.base import EmailUser
UTF8 = 'utf-8'


def default_message(groupInfo):
    m = u'Please accept this invitation to join {0}. I am inviting you '\
        u'because...'
    return m.format(groupInfo.name)


def default_subject(groupInfo):
    r = u'Invitation to join {0} (Action required)'
    retval = r.format(groupInfo.name)
    return retval


class InvitationMessageMixin(object):
    @Lazy
    def supportEmail(self):
        sub = u'Invitation to {0}'.format(self.groupInfo.name)
        m = u'Hi!\n\nI received an invitation to join the group {0}\n    '\
            u'{1}\nand...'
        msg = m.format(self.groupInfo.name, self.groupInfo.url)
        data = {
          'Subject': sub.encode(UTF8),
          'body': msg.encode(UTF8),
        }
        mailto = 'mailto:{0}?{1}'
        retval = mailto.format(self.siteInfo.get_support_email(),
                                urlencode(data))
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


class InvitationMessageText(InvitationMessage, TextMixin):

    def __init__(self, context, request):
        super(InvitationMessageText, self).__init__(context, request)
        filename = 'invitation-to-{0}.txt'.format(self.groupInfo.id)
        self.set_header(filename)

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
        withPara = self.originalMessage.replace(u'\n\n', u'</p><p>')
        withBr = withPara.replace('u\n', u'<br/>')
        retval = '<p>{0}</p>'.format(withBr)
        return retval

    @Lazy
    def txt(self):
        tw = TextWrapper(initial_indent='    ',
                         subsequent_indent='    ')
        retval = ''
        for line in self.originalMessage.splitlines():
            p = tw.fill(line.strip())
            retval = '{0}{1}\n\n'.format(retval, p)
        return retval
