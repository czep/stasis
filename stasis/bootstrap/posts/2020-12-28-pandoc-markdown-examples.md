---
layout: post
title: Pandoc Markdown examples
date: 2020-12-28
topics: pandoc markdown
---

A quick cheatsheet of Markdown examples, using the  [Markdown processing](https://pandoc.org/MANUAL.html#pandocs-markdown).

<!--excerpt-->

Pandoc is a wonderful document conversion tool. I think it is the best Markdown processor available.  Here are some examples of what it can do.  Conveniently, this page can also serve as a handy cheat-sheet for all those times you just can't remember the exact syntax to get Markdown to do what you want it to do.  For complete details, see the [user guide](https://pandoc.org/MANUAL.html#pandocs-markdown).

Pandoc Markdown syntax can be modified by activating different extensions.  If you want to enable or disable certain extensions for your site, change the `PANDOC_ARGS` option in `stasis_config.py`.

# Headings


    # Heading 1
    ## Heading 2
    ### Heading 3
    #### Heading 4
    ##### Heading 5
    ###### Heading 6

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

# Block quotes

    > This is a block quote. This
    > paragraph has two lines.
    >
    > 1. This is a list inside a block quote.
    > 2. Second item.

> This is a block quote. This
> paragraph has two lines.
>
> 1. This is a list inside a block quote.
> 2. Second item.


# Code blocks

## Inline code blocks

    It is possible to apply syntax highlighting to inline code, as in `if not self.has_name: print("Hi!")`{.python} and this will look nice.

It is possible to apply syntax highlighting to inline code, as in `if not self.has_name: print("Hi!")`{.python} and this will look nice.


## Fenced code blocks

    ```python
    def md5(file):
        md5hash = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5hash.update(chunk)
        return md5hash.hexdigest()
    ```python

```python
def md5(file):
    md5hash = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5hash.update(chunk)
    return md5hash.hexdigest()
```


# Unordered lists

    * one
    * two
    * three

* one
* two
* three

## Nested unordered lists

    * fruits
      + apples
        - macintosh
        - red delicious
      + pears
      + peaches
    * vegetables
      + broccoli
      + chard

* fruits
  + apples
    - macintosh
    - red delicious
  + pears
  + peaches
* vegetables
  + broccoli
  + chard



# Ordered lists

    1.  one
    2.  two
    3.  three

1.  one
2.  two
3.  three


# Horizontal rules

    ---

---


# Tables


      Right     Left     Center     Default
    -------     ------ ----------   -------
         12     12        12            12
        123     123       123          123
          1     1          1             1

    Table:  Demonstration of simple table syntax.

  Right     Left     Center     Default
-------     ------ ----------   -------
     12     12        12            12
    123     123       123          123
      1     1          1             1

Table:  Demonstration of simple table syntax.




# Inline formatting

    This text is _emphasized with underscores_, and this
    is *emphasized with asterisks*.


This text is _emphasized with underscores_, and this
is *emphasized with asterisks*.


    This is **strong emphasis** and __with underscores__.

This is **strong emphasis** and __with underscores__.

    This ~~is deleted text.~~

This ~~is deleted text.~~

# Superscripts and subscripts

    H~2~O is a liquid.  2^10^ is 1024.

H~2~O is a liquid.  2^10^ is 1024.



