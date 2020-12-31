import pathlib
import shelve
import datetime
import time
from email import utils
from jinja2 import Environment, FileSystemLoader, select_autoescape
from distutils.dir_util import copy_tree

from .post import Post
from .page import Page
from .pandoc import Pandoc

class Site():
    def __init__(self, args, conf):
        self.config = conf
        self.post_inputs = sorted(pathlib.Path(self.config['DIR_POSTS']).glob('**/*.md'), key=lambda p: str(p.name))
        if args.drafts:
            drafts = list(pathlib.Path(self.config['DIR_DRAFTS']).glob('**/*.md'))
            self.post_inputs = sorted(drafts + self.post_inputs, key=lambda p: str(p.name))
        self.page_inputs = pathlib.Path(self.config['DIR_PAGES']).glob('**/*.md')
        self.posts = []
        self.pages = []
        self.topics = {}
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.config['DIR_TEMPLATES']),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        self.site_path = pathlib.Path('.') / self.config['DIR_PUBLISH']
        self.post_store = shelve.open(self.config['POST_STORE'])
        if args.target == 'prod':
            self.config['SITE']['base_url'] = self.config['SITE']['absolute_url']
        self.pandoc = Pandoc(self.config)

    def build(self):
        self.copystaticfiles()
        self.read_posts()
        self.build_topics()
        self.write_posts()
        self.write_index_pages()
        self.write_topic_pages()
        self.read_pages()
        self.write_pages()
        self.write_rss_feed()
        self.post_store.close()

    def copystaticfiles(self):
        copy_tree(self.config['DIR_STATIC'], self.config['DIR_PUBLISH'])

    def read_posts(self):
        for post_input in self.post_inputs:
            draft = False
            if str(post_input).startswith(self.config['DIR_DRAFTS']):
                draft = True
            if post_input.name in self.post_store:
                post = self.post_store[post_input.name]
                print("Reading from post store: ", post)
            else:
                post = Post(post_input, draft)
            if not post.is_current():
                post.build(self.pandoc, self.config)
                print("Building post: ", post)
            self.posts.append(post)
        self.post_paginate()
        self.store_posts()
        self.config['SITE']['posts'] = self.posts
        print("Read {} posts.".format(str(len(self.posts))))

    def read_pages(self):
        for page_input in self.page_inputs:
            page = Page(page_input)
            page.build(self.pandoc, self.config)
            self.pages.append(page)
        print("Read {} static pages.".format(str(len(self.pages))))

    def post_paginate(self):
        for i, post in enumerate(self.posts):
            if i > 0:
                prev_post = self.posts[i-1]
                post.prev_post = {
                    'url': prev_post.url,
                    'title': prev_post.title
                }
            if i < len(self.posts) - 1:
                next_post = self.posts[i+1]
                post.next_post = {
                    'url': next_post.url,
                    'title': next_post.title
                }

    def store_posts(self):
        for post in self.posts:
            self.post_store[post.input_path.name] = post

    def build_topics(self):
        for post in self.posts:
            for topic in post.topics:
                if topic not in self.topics:
                    self.topics[topic] = []
                self.topics[topic].append(post)
        self.config['SITE']['topics'] = self.topics

    def write_posts(self):
        print("Writing posts...")
        for post in self.posts:
            post.write(self.jinja_env, self.config['SITE'])

    def write_index_pages(self):
        print("Writing index pages...")
        template = self.jinja_env.get_template("index.html")
        post_queue = self.posts.copy()
        post_queue.reverse()
        paginator = {
            'page': 1,
            'n_pages': 1 + int(len(post_queue) / self.config['POSTS_PER_PAGE']),
            'prev_url': None,
            'next_url': None
        }
        while len(post_queue) > 0:
            posts = post_queue[:self.config['POSTS_PER_PAGE']]
            page = {}
            if paginator['page'] == 1:
                index_path = self.site_path / "index.html"
                page['url'] = "/"
            else:
                index_path = self.site_path / "page{}".format(str(paginator['page'])) / "index.html"
                page['url'] = "/page{}/".format(paginator['page'])

            if paginator['page'] + 1 <= paginator['n_pages']:
                paginator['next_url'] = "/page{}/".format(str(paginator['page'] + 1))
            else:
                paginator['next_url'] = None

            if paginator['page'] == 2:
                paginator['prev_url'] = "/"
            elif paginator['page'] > 2:
                paginator['prev_url'] = "/page{}/".format(str(paginator['page'] - 1))
            else:
                paginator['prev_url'] = None

            template_out = template.render(posts=posts, site=self.config['SITE'], page=page, paginator=paginator)
            index_path.parent.mkdir(parents=True, exist_ok=True)
            index_path.write_text(template_out)
            post_queue = post_queue[self.config['POSTS_PER_PAGE']:]
            paginator['page'] += 1


    def write_topic_pages(self):
        print("Writing topic pages...")
        template = self.jinja_env.get_template("topic.html")
        for topic in self.topics:
            print("  {}".format(topic))
            posts = self.topics[topic]
            posts.reverse()
            page = {
                'title': topic.title(),
                'url': "/{}/{}/".format(self.config['TOPICS_URL_PREFACE'], topic)
            }
            template_out = template.render(topic=topic, posts=posts, site=self.config['SITE'], page=page)
            topic_path = self.site_path / self.config['TOPICS_URL_PREFACE'] / topic / "index.html"
            topic_path.parent.mkdir(parents=True, exist_ok=True)
            topic_path.write_text(template_out)

    def write_pages(self):
        print("Writing static pages...")
        for page in self.pages:
            page.write(self.jinja_env, self.config['SITE'])

    def write_rss_feed(self):
        print("Writing RSS feed...")
        # self.config['SITE']['timestamp'] = utils.format_datetime(datetime.datetime.utcnow())
        self.config['SITE']['timestamp'] = self.posts[len(self.posts)-1].date
        template = self.jinja_env.get_template("feed.xml")
        template_out = template.render(site=self.config['SITE'], page={})
        output_path = self.site_path / self.config['SITE']['rssfeed']
        output_path.write_text(template_out)

