===============================
``gs.group.member.invite.base``
===============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Send an invitation to join a group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2013-03-19
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0 New Zealand License`_
  by `OnlineGroups.Net`_.

Introduction
============

This product is concerned with the *issuing* of invitations to join an
online group. Invitations take the form of an email message with a
link. The invitation is responded to using one of the two pages in the
``gs.profile.invite`` module [#profile]_.

Why Invitations?
----------------

For new members the invitation does two things in addition to joining a
person to a group. First, it **verifies** that the email address
works. GroupServer will only be send messages to verified
addresses. Second, the Respond page allows the member to set a password, so
he or she is able to log in.

Even for people that already have profiles, the invitations also allow
*informed consent*. This is not just a good idea, in many countries it is
the law.

Pages
=====

There are two pages provided by this product for issuing invitations:

* `Invite Site Member`_, and 
* `Invite New Member`_ 

Sending invitations in bulk is handled by ``gs.group.member.invite.csv``
[#csv]_.

Invite Site Member
------------------

The page for inviting a site member to join a group,
``admin_invite_site_members.html``, is the simplest. It uses the
``groupserver.InviteMembersNonGroupMembers`` vocabulary to list all the
site members who are not members of the group. The administrator selects
the site members to be invited, and a notification_ is sent to each.

Invite New Member
-----------------

The most commonly used invitation page is used to invite a single person to
join a group: ``admin_join.html``. This page allows the administrator to do
the following.

#. Create a complete profile for the new member, including an email
   address.

#. Customises the notification_ that is sent in the invitation.

If the email address matches a person who already has a profile, then
the person is just sent an invitation; the profile is left as it was.

Notification
============

The notification is split into plain text (``invitationmessage.txt``) and
HTML (``invitationmessage.html``) components. It is complicated by the
administrator being able to write a short message using the `invite new
member`_ page.

The class ``gs.group.member.invite.base.notify.InvitationNotifier``
constructs the email, and uses the ``gs.profile.notify`` [#notify]_ product
to send the message.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.invite.base
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 3.0 New Zealand License:
   http://creativecommons.org/licenses/by-sa/3.0/nz/

.. [#profile] See
              <https://source.iopen.net/groupserver/gs.profile.invite>

.. [#csv] See
          <https://source.iopen.net/groupserver/gs.group.member.invite.csv>

.. [#notify] See           <https://source.iopen.net/groupserver/gs.profile.notify>
