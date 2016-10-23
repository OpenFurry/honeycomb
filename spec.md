Honeycomb Spec
==============

## Overview

Honeycomb is intended to be an art site that caters specifically to the written
word, authors, and readers.  The goal is to create a site that provides the best
experience for uploading or writing works, as well as the best experience for
those who will read the works.  While there may be the ability to upload images
and media, the primary focus should be on stories, articles, novels, and papers.
[honeycomb.cafe](http://honeycomb.cafe), the first implementation, should cater
primarily to the furry subculture.

## Specification

* User management
    * ~~The user should be able to register~~
    * ~~The user should be able to log in and out~~
    * The user should be able to confirm their password *(untested)*
    * The user should be able to change their password *(untested)*
    * ~~The user should be able to change their profile~~
    * The user should be able to change their username *(untested)*
    * ~~The user should be able to add friends~~
    * The user should be able to organize their friends into groups to control
      visibility
    * ~~The user should be able to block other users from viewing their content
      and profile~~ (though any staff bit will override this)
    * The user should be able to belong to a class or classes of users (user,
      content moderator, social moderator, superuser, banned)
        * Users may post submissions, comments, ratings, etc.
        * Content moderators may moderate content (highlight, flag, etc)
        * Social moderators may moderate other users
        * Superusers may do everything
    * Social moderators (maybe content moderators?) and superusers may ban users
    * Users may communicate with each other through messages
    * Users may view a message, which marks it as read
    * Messages show a conversation, not a free-form reply text thingy
    * Users may opt out of messages, except from staff
    * ~~Users may view a list of notifications (comments, faves, promotions,
      moderator highlights, follows, messages, maybe: enjoyed counter,
      ratings)~~
    * ~~Users may delete notifications~~
    * ~~Users may visit user pages at `~(username)`~~
* Posting submissions
    * ~~The user should be able to post a submission as plain text~~
    * ~~The user should be able to post a submission as markdown~~
    * The user should be able to post the submission using a rich text editor
      (TinyMCE?)
    * The user should be able to upload a file
    * The user should be able to upload the two supported default filetypes
      (text/markdown)
    * The user should be able to upload other filetypes (pdf, odt, doc(x), rtf,
      etc.) via pandoc
    * The user should be able to upload a cover image
    * The cover image should be scaled and stored with attribution (name, link, date?)
    * ~~The user should be able to dictate what levels of social interaction
      are allowed with a submission (see "Social interaction")~~
      *(At least enjoy votes)*
* Submission organization
    * ~~The user should be able to set the permissions on a submission (private, followers, world)~~ *(minus followers)*
    * The user should be able to set the visibility on a submission to groups
    * The user should be able to tag the submission with relevant tags
    * The user should be able to tag the submission with global tags ("categories"?),
      such as participant configurations, species, and genre
    * The user should be able to create folders
    * The user should be able to create nested folders
    * The user should be able to add the submission to a folder
    * The user should be able to add the submission to multiple folders
    * The user should be able to upload submissions in order and expect them to be
      displayed in that order when viewed in a folder
    * The user should be able to change the order of submissions in a folder
* Submission viewing
    * ~~The user should be able to view a submission~~ and associated cover image
    * The user should have a pleasant viewing experience on desktop, mobile, and
      print, including distraction-free and inverted modes when selected
    * ~~The user should be able to rate a submission (private, used to
      calculate average rating)~~
    * ~~The user should be able to favorite a submission (public)~~
    * ~~The user should be able to increment a "enjoyed" counter, if the author
      has enabled it~~
    * The user should be able to promote a submission, both as an author and as a
      reader, acting as a vote to float the submission to the top of a promotions
      queue.  Once a submission has been promoted, it remains promoted for a week,
      then is depromoted and prevented from being promoted again
    * Content moderators may select submissions to highlight
    * ~~Users should be able to visit a submission at `~(authorname)/(id)(-(slug))?`~~
* Monetization, ads, and pay-to-promote
    * The user may pay to have their submission promoted, with the same caveat that a
      submission, once promoted, may not be promoted again
    * The user may set up a tip jar, a commission page, a Patreon, or another
      way of monetizing their works
    * The user may pay to have an ad displayed for a period of time
    * The user may see a report of their ad impressions/interactions,
      promotions, highlights, etc on a central page, and, in the latter two
      cases, on the submission itself
* Content discovery and recommendation
    * The user should be able to add favorite tags
    * The user should be able to block tags
    * The user should be able to see recommended submissions based on their
      favorites, calculated by collating the common tags from their favorites
      and displaying submissions with similar tags
    * The user should be able to see recommended submissions based on the submission they
      are currently reading, calculated by the above algorithm, as well as other
      submissions rated similarly by other users
    * The user should be able to specify or search by genre
    * The user should be able to search by tag or content
    * The user should be able to order lists of submissions (from searches, user
      pages, etc) by various criteria (popularity, date, etc)
* Social interaction
    * ~~The user, as a reader, should be able to increment an "enjoyed" counter on
      a submission for each time they've enjoyed the submission, if the author has enabled
      it~~
    * The user, as a reader, should be able to comment on the submission if the
      author has enabled it
    * The user should be able to reply to comments in a nested fashion
    * The user, as an author, should be able to enable or disable comments at
      any time
    * The user, as an author or social moderator, should be able to delete
      comments
    * The user should be able to share a submission, another user, or a publisher on
      various forms of social media
    * ~~The user should be able to link to another user using a syntax;~~ linking thus
      should notify the other user
    * The user should be able to link a twitter account to their profile
    * The user should be able to have new submissions auto-tweeted via linked twitter
      account
    * The site should have its own twitter account that auto-tweets newly-promoted
      or highlighted works
* Publisher pages
    * The user should be able to view a publisher page containing links, logos, and info
      about the the publisher, as well as a list of users who are published by that
      publisher
    * Content moderators should be able to modify a publisher page and add users to the list
      of published authors
    * The user should be able to claim responsibility for a publisher page with proof of
      ownership or employment
    * The user should be able to request to be added to a publisher page as a published
      author, wherein the content moderators and page owner will be able to confirm or deny
      their membership
    * The user should be able to see on a user's profile who they have been published by
