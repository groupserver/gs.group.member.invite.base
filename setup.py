# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
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
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='gs.group.member.invite.base',
    version=version,
    description="The pages that are required to invite people to "
      "join GroupServer groups.",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux"
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='sign up, registration, profile, user, join, invitation',
    author='Michael JasonSmith',
    author_email='mpj17@onlinegroups.net',
    url='http://groupserver.org',
    license='ZPL 2.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.group', 'gs.group.member',
                        'gs.group.member.invite'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
        'sqlalchemy',
        'zope.app.apidoc',
        'zope.browserpage',
        'zope.browserresource',
        'zope.cachedescriptors',
        'zope.component',
        'zope.contentprovider',
        'zope.formlib',
        'zope.interface',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.schema',
        'zope.sqlalchemy',
        'zope.tal',
        'zope.tales',
        'zope.viewlet',
        'Zope2',
        'gs.content.email.base',
        'gs.content.form',
        'gs.content.js.wymeditor[zope]',
        'gs.content.layout',
        'gs.database',
        'gs.group.base',
        'gs.group.member.base',
        'gs.group.member.viewlet',
        'gs.help',
        'gs.profile.email.base',
        'gs.profile.notify',
        'gs.site.member',
        'Products.CustomUserFolder',
        'Products.GSAuditTrail',
        'Products.GSContent',
        'Products.GSGroup',
        'Products.GSGroupMember',
        'Products.GSProfile',
        'Products.XWFCore',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
