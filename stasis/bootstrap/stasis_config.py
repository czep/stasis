# Starter configuration file copied on init

### local directory setup
DIR_PUBLISH   = "_pub"
DIR_POSTS     = "posts"
DIR_PAGES     = "pages"
DIR_DRAFTS    = "drafts"
DIR_STATIC    = "static"
DIR_TEMPLATES = "templates"
POST_STORE    = "post_store.db"

### public-facing site metadata
SITE = {
    'title':        "Stasis",
    'description':  "A simple static site generator with deployment to S3/Cloudfront",
    'site_name':    "example.com",
    'author':       ("author", "/about/"),
    'author_name':  "Namely McNameworthy",
    'absolute_url': "https://example.com",
    'base_url':     "",
    'twitter':      "@example",
    'github':       "https://github.com/example",
    'links': [
        ("Home", "/"),
        ("About", "/about/"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Main_Page"),
        ("RSS Feed", "/feed.xml"),
        ("README", "/readme/")
    ],
    'recent_posts': 10,
    'maincss':      "/css/main.css",
    'rssfeed':      "feed.xml"
}

PANDOC_ARGS = "markdown+backtick_code_blocks+inline_code_attributes"
EXCERPT_SEPARATOR = "<!--excerpt-->"
TOPICS_URL_PREFACE = "topics"

### pagination
POSTS_PER_PAGE = 10

### development server
SERVER_PORT = 9988

### deployment
AWS_PROFILE = "aws_profile_name"
S3_BUCKET = "s3_bucket_name"
S3_USE_GZIP = True
S3_GZIP_COMPRESSION = 9
S3_GZIP_FILES = [
    "*.html",
    "*.css",
    "*.js",
    "*.txt"
]
S3_GZIP_MINSIZE = 1024

### files matching these patterns will never be updated or deleted from S3
IGNORE_ON_SERVER = [
    "legacy*",
    "contact.html",
]

### files matching these patterns will bever be uploaded to S3
EXCLUDE_FROM_UPLOAD = [
    "*.DS_Store",
    "*.upload",
]

# Default format for post urls: "/YYYY/MM/DD/slug/"
def FN_POST_URL(args):
    url = "/{}/{}/{}/{}/".format(
        args['meta']['date'].strftime("%Y"),
        args['meta']['date'].strftime("%m"),
        args['meta']['date'].strftime("%d"),
        args['input_path'].stem[11:]
    )
    return url


