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
from zope.schema import ASCIILine, Bool, Choice, List, Text, TextLine
from zope.interface.interface import Interface
from Products.GSProfile.interfaces import deliveryVocab


class IGSInvitationMessage(Interface):
    text = Bool(title='Text',
        description='Display the invitation as pure text, rather than '
            'a HTML pre-element. Call it command  coupling if you '
            'want, it is how the code works.',
        required=False,
        default=False)

    preview = Bool(title='Preview',
          description='True if the message is a preview.',
          required=False,
          default=False)

    toAddr = TextLine(title='To',
        description='The email address of the person receiving the '
            'invitation.',
        required=False)

    fromAddr = TextLine(title='To',
        description='The email address of the person sending the '
            'invitation.',
        required=False)

    supportAddr = TextLine(title='Support',
        description='The email address of the support-group.',
        required=False)

    subject = TextLine(title='Subject',
        description='The subject-line of the invitation.',
        required=False)

    body = Text(title='Body',
        description='The body of the invitation.',
        required=True)

    invitationId = ASCIILine(title='Invitation Identifier',
        description='The identifier for the invitation to join the '
            'group',
        required=False,
        default='example'.encode('ascii'))


pageTemplatePath = 'browser/templates/invitationmessagecontentprovider.pt'


class IGSInvitationMessageContentProvider(IGSInvitationMessage):
    pageTemplateFileName = ASCIILine(title='Page Template File Name',
          description='The name of the ZPT file that is used to '
            'render the status message.',
          required=False,
          default=pageTemplatePath.encode('ascii'))

    message = Text(title='Invitation Message',
        description='The message that appears at the top of the email '
            'invitation to the new group member. The message will '
            'appear before the link that allows the recipient to '
            'accept or reject the invitation.',
        required=True)


class IGSInvitationFields(Interface):
    message = Text(title='Invitation Message',
        description='The message that appears at the top of the email '
            'invitation to the new group member. The message will '
            'appear before the link that allows the member to accept '
            'or reject the invitation.',
        required=True)

    fromAddr = Choice(title='Email From',
      description='The email address that you want in the "From" '
        'line in the invitation tat you send.',
      vocabulary='EmailAddressesForLoggedInUser',
      required=True)

    delivery = Choice(title='Group Message Delivery Settings',
      description='The message delivery settings for the new user',
      vocabulary=deliveryVocab,
      default='email')

    subject = TextLine(title='Subject',
        description='The subject line of the invitation message that '
            'will be sent to the new member',
        required=True)


class IGSInviteSiteMembers(IGSInvitationFields):
    site_members = List(title='Site Members',
      description='The members of this site that are not a member of '
        'this group.',
      value_type=Choice(title='Group',
                      vocabulary='groupserver.InviteMembersNonGroupMembers'),
      unique=True,
      required=True)
