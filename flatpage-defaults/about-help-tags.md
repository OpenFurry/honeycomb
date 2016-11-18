## All about tags

Tags are a very general way to categorize submissions.  A submission can have many tags, and a tag can belong to many submissions.  This means that you can describe what's happening in a submission through the use of tags.  For instance, you could say that your submission is fiction, involves romance between a homosexual couple and has violence (but not between the members of the relationship).  You can get as general or as specific as you want with tags.

A lot of different sites have tags like this, whether they call them 'categories' on a news site or 'hashtags' on Twitter.  Honeycomb allows you to do a few neat things with tags, however.

Of course, you can list all tags on the site within a tag cloud, which shows tags according to size, where the more popular a tag is, the larger the text is.  You can list all submissions tagged with a certain tag, as well, which lets you find submissions that might also contain something that you enjoy.

To that end, you can favorite tags on Honeycomb.  This lets you follow submissions that contain topics that you like.  For instance, you could favorite 'science fiction', 'foxes', and 'humor', and easily have a list of submissions that fall under one or more of those tags.

Not everyone likes everything, though, and to that end, Honeycomb allows you to block a tag.  For instance, if you just *hate* science fiction, you could block that tag and then submissions tagged with 'science fiction' would no longer show up in lists of submissions for you (though you'll still be able to view a submission with blocked tags directly, if someone provides you with the link).  Of course, you can remove favorites and submissions to change the way you view submissions.

## Tagging submissions

Honeycomb uses a tagging system called *taggit*.  Taggit allows you to tag in several ways!  You can tag your submissions as a comma separated list of tags - if you need to use a comma in a tag for some reason, you can wrap the tag in quotes (e.g: `"look ma, no hands"`) - or, if you want to be super simple, by just a space-delimited set of words.  The tagging system is fairly flexible, and treats tag inputs like such:

Tag input string | Resulting tags | Notes
---|---|---
apple ball cat | <ul><li>apple</li><li>ball</li><li>cat</li></ul> | No commas, so space delimited
apple, ball cat | <ul><li>apple</li><li>ball cat</li></ul> | Comma present, so comma delimited
"apple, ball" cat dog | <ul><li>apple, ball</li><li>cat</li><li>dog</li></ul> | All commas are quoted, so space delimited
"apple, ball", cat dog | <ul><li>apple, ball</li><li>cat dog</li></ul> | Contains an unquoted comma, so comma delimited
apple "ball cat" dog | <ul><li>apple</li><li>ball cat</li><li>dog</li></ul> | No commas, so space delimited
"apple" "ball dog | <ul><li>apple</li><li>ball</li><li>dog</li></ul> | Unclosed double quote is ignored

As one of the primary focuses of Honeycomb is content discoverability, tags are **required** on all submissions.  This is to help people find new works, as well as to hide works which they do not wish to see (this applies only to submission lists, though, such as user submissions, user favorites, and tag and genre lists; it does not apply to search results, nor does it apply to viewing submissions - and, of course, it does not apply to logged-out users).

## Categories

Honeycomb also supports a special class of tags using the existing tag system.  These tags are implemented as categories which allow readers to visit special pages to see what subcategories there are.  Some examples are:

* Genre
    * Sci-fi
    * Horror
    * Fantasy
    * Romance
    * Fiction
    * Non-fiction
    * etc.
* Rating
    * G
    * PG-13
    * R
    * NC-17
    * etc.
* Content warnings
    * Gore
    * Violence
    * etc.

Although one may still tag as one wishes, including within these categories, these provide a shortcut to use in viewing on pages, as well as in creating or editing submissions.

Categories are super simple, and just take the form of `<category>:<subcategory>` (e.g: `genre:sci-fi`).  Which categories are implemented is up to the site admins.  *Site owner:* The currently supported special tags are:

* `genre:`
* `rating:`
* `content-warning:`

If you don't see the category you want in the category dropdowns on the submission create/edit page, you can create the one you need by entering it in the tags field (e.g: if the technical writing genre doesn't exist, you can add it by tagging your submission `"genre:technical writing"`).  This feature shouldn't be abused, and content moderators may remove categories that misuse this system.
