Honeycomb Spec
==============

## Overview

Honeycomb is intended to be an art site that caters specifically to the written
word, authors, and readers.  The goal is to create a site that provides the best
experience for uploading or writing works, as well as the best experience for
those who will read the works.  While there may be the ability to upload images
and media, the primary focus should be on stories, articles, novels, and papers.
honecomb.cafe, the first implementation, should cater primarily to the furry
subculture.

## Specification

* User management
    * The user should be able to register
    * The user should be able to log in and out
    * The user should be able to confirm their password
    * The user should be able to change their password and profile
    * The user should be able to change their username
    * The user should be able to add friends
    * The user should be able to organize their friends into groups to control
      visibility
    * The user should be able to belong to a class or classes of users (user,
      content moderator, social moderator, superuser, banned)
        * Users may post stories, comments, ratings, etc.
        * Content moderators may moderate content (highlight, flag, etc)
        * Social moderators may moderate other users
        * Superusers may do everything
* Posting stories
    * The user should be able to post a story as plain text
    * The user should be able to post a story as markdown
    * The user should be able to post the story using a rich text editor (TinyMCE?)
    * The user should be able to upload a file
    * The user should be able to upload the two supported default filetypes
      (text/markdown)
    * The user should be able to upload other filetypes (pdf, odt, doc(x), rtf,
      etc.) via pandoc
    * The user should be able to upload a cover image
    * The cover image should be scaled and stored with attribution (name, link, date?)
    * The user should be able to dictate what levels of social interaction are
      allowed with a story (see "Social interaction")
* Story organization
    * The user should be able to set the permissions on a story (private, followers, world)
    * The user should be able to set the visibility on a story to groups
    * The user should be able to tag the story with relevant tags
    * The user should be able to tag the story with global tags ("categories"?),
      such as participant configurations, species, and genre
    * The user should be able to create folders
    * The user should be able to create nested folders
    * The user should be able to add the story to a folder
    * The user should be able to add the story to multiple folders
    * The user should be able to upload stories in order and expect them to be
      displayed in that order when viewed in a folder
    * The user should be able to change the order of stories in a folder
* Story viewing
    * The user should be able to view a story and associated cover image
    * The user should be able to rate a story (public, used to calculate average
      rating)
    * The user should be able to favorite a story (private)
    * The user should be able to increment a "enjoyed" counter, if the author
      has enabled it
    * The user should be able to promote a story, both as an author and as a
      reader, acting as a vote to float the story to the top of a promotions
      queue.  Once a story has been promoted, it remains promoted for a week,
      then is depromoted and prevented from being promoted again
    * Content moderators may select stories to highlight
* Monetization, ads, and pay-to-promote
    * The user may pay to have their story promoted, with the same caveat that a
      story, once promoted, may not be promoted again
    * The user may set up a tip jar, a commission page, a Patreon, or another
      way of monetizing their works
    * The user may pay to have an ad displayed for a period of time
* Content discovery and recommendation
    * The user should be able to add favorite tags
    * The user should be able to block tags
    * The user should be able to see recommended stories based on their
      favorites, calculated by collating the common tags from their favorites
      and displaying stories with similar tags
    * The user should be able to see recommended stories based on the story they
      are currently reading, calculated by the above algorithm, as well as other
      stories rated similarly by other users
    * The user should be able to specify or search by genre
    * The user should be able to search by tag or content
    * The user should be able to order lists of stories (from searches, user
      pages, etc) by various criteria (popularity, date, etc)
* Social interaction
    * The user, as a reader, should be able to increment an "enjoyed" counter on
      a story for each time they've enjoyed the story, if the author has enabled
      it
    * The user, as a reader, should be able to comment on the story if the
      author has enabled it
    * The user should be able to reply to comments in a nested fashion
    * The user, as an author, should be able to enable or disable comments at
      any time
    * The user, as an author or social moderator, should be able to delete
      comments
