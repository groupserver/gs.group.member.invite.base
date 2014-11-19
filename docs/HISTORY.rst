Changelog
=========

5.2.0 (2014-11-19)
------------------

* Sorting the site members listed on the *Invite site members*
  page by name

5.1.0 (2014-09-24)
------------------

* Switching to GitHub_ as the primary repository, and naming the
  reStructuredText files as such
* Ensuring Unicode

.. _GitHub: https://github.com/groupserver/gs.group.member.invite.base

5.0.2 (2014-06-19)
------------------

* Following the core form code to :module:`gs.content.form.base`

5.0.1 (2014-02-28)
------------------

* Ensuring the headers are ASCII

5.0.0 (2014-01-31)
------------------

* Moving the code for re-sending an invitation to
  :module:`gs.group.member.invite.resend`

4.3.0 (2013-11-19)
------------------

* Adding the WYMeditor_ to the *Invite* page

.. _WYMeditor: http://www.wymeditor.org/

4.2.1 (2013-10-23)
------------------

* Code cleanup

4.2.0 (2013-10-07)
------------------

* Rely on the new `gs.content.email.*` products to handle the
  HTML notifications

4.1.0 (2013-09-04)
------------------

* Moved :file:`processor` here from
  :module:`gs.group.member.invite.json`

4.0.0 (2013-08-09)
------------------

* Update for the new UI
* Fixing the :mailheader:`Content-type` headers
* Refactored the JavaScript

3.4.0 (2013-03-20)
------------------

* Massive code tidy

3.3.0 (2013-01-22)
------------------

* Making the links relative to the base of the site
* Switching ``@property`` decorators over to ``@Lazy``
* Code cleanup

3.2.0 (2012-07-05)
------------------

* UI update of the *Invite site members* page
* UI update of the *Resend invitation* page
* UI update of the *Invite a new member* page

3.1.0 (2012-06-22)
------------------

* SQLAlchemy update

3.0.0 (2012-05-15)
------------------

* Moved the code to the :module:`gs.group.member.invite.base`
  namespace, from the :module:`gs.group.member.invite` namespace

2.4.0 (2012-03-08)
------------------

* Moving the ``groupserver.InviteMembersNonGroupMembers`
  vocabulary here from :module:`Products.GSGroupMember`
* Setting the friendly name in the :mailheader:`To` header of the
  preview


2.3.1 (2012-02-09)
------------------

* Stop sending the fake header when emailing the invitation

2.3.0 (2012-01-17)
------------------

* Switch to use a more typical notifier for the invation
* Use :class:`gs.group.base.GroupForm` as the base

2.2.0 (2011-06-06)
------------------

* Using the new MessageSender class
* Removing the :mailheader:`Reply-to`
* Removing the link to the *Invite by CSV* page

2.1.2 (2011-05-19)
------------------

* Adding the :guilabel:`Invite member` links to the
  :guilabel:`Admin` tab on the group page

2.1.1 (2011-04-27)
------------------

* Handle a full email address

2.1.0 (2011-01-26)
------------------

* Update to follow the new ``gs.profile.email.base`` product
* Committing transactions
* Dealing with old ``XFrom`` code

2.0.0 (2010-12-20)
------------------

* Switch to jQuery UI classes
* Better field hiding
* Moved page-specific CSS to the global stylesheet
* Using the new form-message content provider
* Making the SQL quiet on install

1.3.1 (2010-10-18)
------------------

* Be more robust when the invited member lacks a verified email
  address

1.3.0 (2010-09-23)
------------------

* Show the name and address of the invited member where it makes
  sense
* Added a *Resend invitation page*
* Hide most of the profile fields, as they are optional

1.2.1 (2010-09-07)
------------------

* Bugfix

1.2.0 (2010-08-19)
------------------

* Setting better defaults, including the :mailheader:`From`
  address
* Context and interface fixes

1.1.0 (2010-07-30)
------------------

* Handle withdrawn invitations
* Work with skins better
* Setting delivery for *Admin join*

1.0.0 (2010-07-23)
------------------

* Initial release
