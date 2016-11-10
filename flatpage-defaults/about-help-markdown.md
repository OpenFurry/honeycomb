Honeycomb lets users write with rich formatting in several different places.  Submissions, obviously, but also in comments, in user profiles, in content flags, bans, applications, publisher pages...just about anywhere you see a big textbox, markdown is welcome!

Markdown is a simple way to format your text for the web so that it's readable both when rendered in the browser and as plaintext.  Honeycomb supports basic formatting, plus several extensions, as listed below:

* [Base features](#base-features)
    * [Basic paragraphs and line breaks](#basic-paragraphs-and-line-breaks)
    * [Headers](#headers)
    * [Lists](#lists)
    * [Emphasis](#emphasis)
    * [Links](#links)
    * [Images](#images)
    * [Code and preformatted text](#code-and-preformatted-text)
    * [Block quotes](#block-quotes)
    * [Horizontal rule](#horizontal-rule)
* [Extensions](#extensions)
    * [Tables](#tables)
    * [Footnotes](#footnotes)
    * [Abbreviations](#abbreviations)
    * [Additional formatting](#additional-formatting)
    * [Honeycomb markdown extensions](#honeycomb-markdown-extensions)
    * [Smart symbols](#smart-symbols)
    * [CodeHilite and SuperFences](#codehilite-and-superfences)

## Base features

Markdown comes with a list of basic features that every implementation should support.  These are listed here.  For additional features beyond the basics, make sure to check out the [extensions](#extensions).

### Basic paragraphs and line breaks

You can write in markdown as you would in just about any text document.  Every line is its own paragraph, just like this.

```
You can write in markdown as you would in just about any text document.  
Every line is its own paragraph, just like this.
```

To start a new paragraph, you can just hit enter twice at the end of your old paragraph.

This lets paragraphs read naturally in text as well as on the web.

```
To start a new paragraph, you can just hit enter twice at the end of your old
paragraph.

This lets paragraphs read naturally in text as well as on the web.
```

You can also cause a linebreak in the  
middle of a line without starting a new paragraph by only adding one newline instead of two, and adding two spaces at the end of the previous line.

```
You can also cause a linebreak in the<space><space>
middle of a line without starting a new paragraph by only adding one newline
instead of two, and adding two spaces at the end of the previous line.
```

If you don't add the spaces at the end
of the line, markdown will consider the
lines as part of the same paragraph, so
you can write within restricted line
lengths.

```
If you don't add the spaces at the end
of the line, markdown will consider the
lines as part of the same paragraph, so
you can write within restricted line
lengths.
```

---

### Headers

Sometimes you need to break your code up into sections, and for that you often need a header at the start of each section.

For something like this:
:  
    # My great book

    ## Introduction

    I wrote this book in one sitting when I was two and a half years old.

    ### Acknowledgements

    I'd like to thank my mom, who helped me hold the pen.

    ## Chapter 1

    ### Section 1

    #### Subsection 1

    ##### Subsubsection 1

    ###### Subsubsubsection 1

    I really like having six nested subsections

You would write:
:  
    ```markdown
    # My great book

    ## Introduction

    I wrote this book in one sitting when I was two and a half years old.

    ### Acknowledgements

    I'd like to thank my mom, who helped me hold the pen.

    ## Chapter 1

    ### Section 1

    #### Subsection 1

    ##### Subsubsection 1

    ###### Subsubsubsection 1

    I really like having six nested subsections
    ```

You can only go up to six deep, sorry :)  For the first two, you can underline them for something a bit more natural:
:  
    My great book
    =============

    Introduction
    ------------

    ### Acknowledgements

You can also write:
:  
    ```markdown
    My great book
    =============

    Introduction
    ------------

    ### Acknowledgements
    ```

*NB:* This includes `pymdownx.headeranchor`, which will make each header linkable, as in this document, with a link appearing when you hover over the header.

---

### Lists

You can also do some common list tasks within markdown, such as bulleted lists:

* One
* Two
* Apple

```markdown
* One
* Two
* Apple
```

Numbered lists:

1. Seven
2. Eight
3. Q

```markdown
1. Seven
2. Eight
3. Q
```

And even nested lists of various types:

* One
    * The loneliest number
    * That you'll ever do
* Two
    1. Almost as bad as one
        * Really, it's the loneliest number since the number one.
    2. Did you know that a solar system with two suns is called a binary system?
    3. It's true.

```markdown
* One
    * The loneliest number
    * That you'll ever do
* Two
    1. Almost as bad as one
        * Really, it's the loneliest number since the number one.
    2. Did you know that a solar system with two suns is called a binary system?
    3. It's true.
```

*NB:* This includes `pymdownx.definitionlists`, which allow definition style lists like the ones in this document:

Topic 1
:   Definition 1

Topic 2
:   Definition 2

```markdown
Topic 1
:   Definition 1

Topic 2
:   Definition 2
```

---

### Emphasis

Emphasizing text in various ways is also available.  You can make it **strong** or *italic* with asterisks, or even __strong__ or _italic_ with underscores.

```markdown
Emphasizing text in various ways is also available.  You can make it
**strong** or *italic* with asterisks, or even __strong__ or _italic_ with
underscores.
```

*NB:* This includes `pymdownx.betterem`, which makes working with nested emphasis a little easier.  For more information on what exactly that means, see the [betterem docs](https://facelessuser.github.io/pymdown-extensions/extensions/betterem/).

---

### Links

If you'd like to include links in your text, that's super easy too.  You can link with [any text you want](https://github.com/OpenFurry/honeycomb).

```markdown
If you'd like to include links in your text, that's super easy too.  You can
link with [any text you want](https://github.com/OpenFurry/honeycomb).
```

If you're going to be typing the [same][url] [URL][url] [over][url] and [over][url] [again][url], you can create a shortcut to that url for using rather than taking up space with the link.  You can put the shortcut definition anywhere after it's used.

[url]: https://honeycomb.cafe

```markdown
If you're going to be typing the [same][url] [URL][url] [over][url] and
[over][url] [again][url], you can create a shortcut to that url for using
rather than taking up space with the link.  You can put the shortcut
definition anywhere after it's used.

[url]: https://honeycomb.cafe
```

*NB:* This includes `pymdownx.magiclink`, which will link a plain URL, or a URL in brackets:

For
:   https://honeycomb.cafe or <https://honeycomb.cafe>

Type
:   `https://honeycomb.cafe` or `<https://honeycomb.cafe>`

---

### Images

Honeycomb itself doesn't support hosting any images beyond submission icons and covers, but if *you* host an image, it's simple to include it!

![OpenFurry](http://openfurry.org/of-icon.png){: style="width: 30px" } - It's For Cats(tm)

```markdown
Honeycomb itself doesn't support hosting any images beyond submission icons
and covers, but if *you* host an image, it's simple to include it!

![OpenFurry](http://openfurry.org/of-icon.png) - It's For Cats(tm)
```

Is your image too big?  Attribute lists are also supported:

```markdown
![OpenFurry](http://openfurry.org/of-icon.png){: style="width: 30px" }
```

---

### Code and preformatted text

Insert code, preformatted text, and similar monospaced text with backticks.

You can have `inline code comments` that show something is a command, or maybe a robot speaking.

```markdown
You can have `inline code comments` that show something is a command, or
maybe a robot speaking.
```

Or you can have blocks of preformatted texts:

```
14 My dove in the clefts of the rock,
    in the hiding places on the mountainside,
show me your face,
    let me hear your voice;
for your voice is sweet,
    and your face is lovely.
15 Catch for us the foxes,
    the little foxes
that ruin the vineyards,
    our vineyards that are in bloom.
```

Which you'd create with:

```markdown
 ```
 14 My dove in the clefts of the rock,
     in the hiding places on the mountainside,
 show me your face,
     let me hear your voice;
 for your voice is sweet,
     and your face is lovely.
 15 Catch for us the foxes,
     the little foxes
 that ruin the vineyards,
     our vineyards that are in bloom.
 ```
```

Or indent the text you want preformated by four spaces (dots representing spaces)

```
....14 My dove in the clefts of the rock,
........in the hiding places on the mountainside,
....show me your face,
........let me hear your voice;
....for your voice is sweet,
........and your face is lovely.
....15 Catch for us the foxes,
........the little foxes
....that ruin the vineyards,
........our vineyards that are in bloom.
```

---

### Block quotes

> Need to quote something at length?  You can use a blockquote for that.
>
> Note that the same rules for paragraphs apply:  
> If you want a line break early, you'll need the two spaces at the end.

```markdown
> Need to quote something at length?  You can use a blockquote for that.
>
> Note that the same rules for paragraphs apply:<space><space>
> If you want a line break early, you'll need the two spaces at the end.

```

---

### Horizontal rule

You can include a horizontal rule like the one just below this paragraph by entering three or more dashes on their own line with a blank line to the top and bottom:

```markdown

-------

```

---

## Extensions

We've just gone over what goes into stock markdown, but the format is definitely extensible, and we've added quite a few add-ons to add more features.

### Tables

Tables are provided through `pymdownx.tables`:

Markdown | Result
---------|-------
`*em*`   | *em*

```
Markdown | Result
---------|-------
`*em*`   | *em*
```

You don't need to be super neat on these, either, so long as the header indicator has at least three dashes per cell and a space around every cell border:

One | Two?! | idk like a gajillion
---|---|---
1 | 2 | 128947908156316981

```
One | Two?! | idk like a gajillion
---|---|---
1 | 2 | 128947908156316981
```

---

### Footnotes

Footnotes are provided through `pymdownx.footnotes`:

Some complicated topic[^1] that needs a reference[^show your work]

`Some complicated topic[^1] that needs a reference[^show your work]`

And then, at some point later in your work (doesn't need to be the bottom), reference the footnotes with:

```
[^1]: It's probably about dogs
[^show your work]: Look, the reference is even written by a dog!
```

[^1]: It's probably about dogs
[^show your work]: Look, the reference is even written by a dog!

---

### Abbreviations

Abbreviations are included as well:

The HTML specifications is maintained by the W3C.

```
The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium
```

---

### Additional formatting

PyMdownX includes some additional formatting options:

==Highlighted text==

```markdown
==Highlighted text==
```

~~Deleted text~~

```markdown
~~Deleted text~~
```

---

### Honeycomb Markdown Extensions

Honeycomb comes with some of its own markdown options. *Site owner: replace with a real user*

Image only: @!makyo

```
Image only: @!makyo
```

Image and name: @makyo

```
Image and name: @makyo
```

Just name: ~makyo

```
Just name: ~makyo
```

---

### Smart symbols

One extension includes some shortcuts to commonly used symbols:

Markdown | Result
---|---
`(tm)` | (tm)
`(c)` | (c)
`(r)` | (r)
`c/o` | c/o
`+/-` | +/-
`-->` | -->
`<--` | <--
`<-->` | <-->
`=/=` | =/=
`1/4, etc` | 1/4, etc
`1st, 2nd, etc` | 1st, 2nd, etc

---

### CodeHilite and SuperFences

Highlight your code with syntax highlighting (for languages in [this list](http://pygments.org/languages/), perhaps fewer depending on the version of pygments installed):

```python
def foo(bar):
    print(bar)
```

```markdown
    ```python
    def foo(bar):
        print(bar)
    ```
```

*NB:* If you're going to use superfences in lists (as above), you must put the fence on a new line, but don't forget to put spaces (represented by dots) after your list indicators:

* List one
*  
  ```python
  def foo(bar):
      print(bar)
  ```

or

Term
:  
   ```
   definition
   ```

```markdown
 * List one
 * ..
   ```python
   def foo(bar):
       print(bar)
   ```

or

Term
:..
    ```
    definition
    ```
```
<!--
```
-->

<!-- Footnotes -->
*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium
