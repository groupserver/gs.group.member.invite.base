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
import md5
from time import asctime
from Products.GSGroupMember.groupmembership import userInfo_to_user
from Products.XWFCore.XWFUtils import convert_int2b62


def set_digest(userInfo, groupInfo, data):
    delivery = 'delivery'
    email = 'email'
    digest = 'digest'
    web = 'web'
    if not delivery in data:
        m = '"{0}" not in data'.format(delivery)
        raise ValueError(m)
    if data[delivery] not in [email, digest, web]:
        m = 'Invalid delivery setting: "{0}"'.format(data[delivery])
        raise ValueError(m)
    user = userInfo_to_user(userInfo)
    assert hasattr(user, 'set_enableDigestByKey')

    if data[delivery] == email:
        # --=mpj17=-- The default is one email per post
        pass
    elif data[delivery] == digest:
        user.set_enableDigestByKey(groupInfo.id)
    elif data[delivery] == web:
        user.set_disableDeliveryByKey(groupInfo.id)


def invite_id(siteId, groupId, userId, adminId, miscStr=''):
    print siteId
    print groupId
    print 'User ID %s' % userId
    print adminId
    print miscStr
    istr = asctime() + siteId + groupId + userId + adminId + miscStr
    print
    print istr
    print
    istr = asctime() + siteId + groupId + userId + adminId + miscStr
    inum = long(md5.new(istr).hexdigest(), 16)
    retval = str(convert_int2b62(inum))
    assert retval
    assert type(retval) == str
    return retval
