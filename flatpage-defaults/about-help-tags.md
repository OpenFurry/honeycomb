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
