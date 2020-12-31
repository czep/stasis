# Stasis

A simple static site generator with deployment to S3/Cloudfront.

## Features

Stasis is a static website generator written in Python, using [Pandoc](https://pandoc.org/) to convert Markdown documents to html rendered with [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) templates, and optionally deploying to Amazon S3 and Cloudfront.

Stasis is designed to mimic the workflow offered by Jekyll and is mainly targeted at personal blogs. The feature set is quite basic, but this also makes the program easy to understand and extend to fit your needs.

* Conversion of Markdown posts to html, with Pandoc extensions available at your discretion.
* Workflow similar to Jekyll:  init, clean, build, serve, deploy.
* Easy to use templates with Jinja2.
* A basic development server for previewing the site locally.
* Index pages with pagination.
* Static or "flat" pages, also written in Markdown and rendered to a specified url (eg. about, contact, 404).
* A sidebar with links, recent posts, and topics.
* Topic pages.
* RSS feed generation.
* Deployment to S3 with dry-run, ignore on server, exclude from upload, and Cloudfront invalidation.
* Static file pass-through for CSS, Javascript, media, and legacy content.
* Purely static html output.

For more detail and background, please see my blog post about [why I wrote Stasis](https://czep.net/20/stasis.html).


## Install

First, [install Pandoc](https://pandoc.org/installing.html) following the documentation for your system.

To install the latest distribution of Stasis from PyPI, install using pip.  The install will create a console script called `stasis`, so I recommend doing this within a virtual environment.

    pip install stasis-ssg

Alternatively, for the latest source code, clone this repository first and then install the package from a local working directory, for example:

    mkdir stasis-devel && cd $_
    mkdir .venv
    python3 -m venv .venv/stasis
    source .venv/stasis/bin/activate

    git clone https://github.com/czep/stasis.git .
    pip install -e .

Run `stasis -v` to verify that the install worked.

## Use

After installation, create a new working directory in which to develop your site.  Make sure this is a new empty directory:

    mkdir ~/mysite && cd $_
    stasis init

The `init` command will create a basic starter site in the current directory.  The default setup will look like this:

    ├── _pub                # target location for building the site and staging for deployment
    ├── drafts              # optional drafts folder
    ├── pages               # static pages
    ├── posts               # markdown posts
    ├── stasis_config.py    # configuration options
    ├── static              # files to be copied directly to _pub
    └── templates           # Jinja2 templates

After initializing the site, the next steps are:

* Edit `stasis_config.py` to customize your site's metadata and other configuration options.
* Edit the templates to get the layout you want.
* Copy your CSS file to `static/css/main.css`.  Add any additional static files to the `static` directory.  These will be copied to `_pub` without being processed.
* Add static pages to the `pages` directory.
* Add posts to the `posts` directory.

These commands will help you build and deploy your site:

    stasis build
    stasis clean
    stasis build --target=prod
    stasis serve
    stasis deploy --dry-run
    CLOUDFRONT_ID=EXXXXXXXXXXXXX stasis deploy

### build

Running `stasis build` alone or with the development target `stasis build --target=dev` will generate the site with relative links.  Internal `<a>` and `<img>` tags will begin with `/`.  This makes it easier to navigate through the site when serving it locally.  Building with the production target `stasis build --target=prod` will prepend the site's baseurl defined in `stasis_config.py` to all links, making them absolute instead of relative.  This is likely what you will want to do before deployment to ensure that all of your links point to their respective canonical pages.

To build the site with drafts enabled, run:

    stasis build --drafts

### clean

At any point if you want to do a fresh rebuild, run `stasis clean`. This will delete everything in `_pub` as well as the cached posts in `post_store.db`.

### serve

Start a very simple web server to preview your site.  Unlike in Jekyll, there is not an option to serve the site with or without drafts.  The server will simply show you whatever has been built in the `_pub` directory.

### deploy

Before trying to deploy, change the `AWS_PROFILE` and `S3_BUCKET` config options.  I recommend creating a new profile that has S3 Read/Write permission as well as permission to invalidate your Cloudfront distribution.  Add this profile to your `~/.aws/credentials`.

The first time you try to deploy, please do so with the `--dry-run` argument to make sure the the results are what you expect.  Dry run will connect to your S3 bucket, compare local and remote files, and print an output containing three sections:

1. New files to upload to S3
2. Modified files to upload to S3
3. Old files to delete from S3

Examine the list before running without the dry-run option.  In `stasis_config.py`, there are two pattern lists that can help control what is and is not deployed: `IGNORE_ON_SERVER` specifies patterns that will not be added, modified, or deleted.  Use this for any legacy content that you want to manage manually.  `EXCLUDE_FROM_UPLOAD` specifies patterns that will not be uploaded to S3 from your local filesystem.

By default, stasis will compress most text files before uploading.  This can be toggled with the `S3_USE_GZIP` config option.  If True, for all files that meet the gzip criteria, a copy will be created with an extension of ".upload".  This is simply a gzipped copy of the original file and is only used during the deployment process.  However, you must keep the pattern `"*.upload"` in `EXCLUDE_FROM_UPLOAD` to prevent these files from also being uploaded.

When ready to deploy, pass your cloudfront distribution ID as an environment variable:

    CLOUDFRONT_ID=EXXXXXXXXXXXXX stasis deploy

After deploying to S3, this will start a root-level wild-card invalidation `'/*'`.  If you do not want stasis to do the invalidation for you, or if you are not using Cloudfront at all, simply run:

    stasis deploy

This will deploy to S3 but will not attempt a Cloudfront invalidation.



