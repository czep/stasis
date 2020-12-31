import pathlib
import datetime

import frontmatter

class BasePage():
    def __init__(self, input_path):
        self.input_path = input_path
        self.output_path = None
        self.layout = None
        self.url = None
        self.title = ""
        self.date = None
        self.wordcount = 0
        self.topics = []
        self.content_text = None
        self.content_html = None
        self.excerpt_text = None
        self.excerpt_html = None

    def build(self, pandoc, config):
        with self.input_path.open() as infile:
            self.content_text = infile.read()
        meta = frontmatter.loads(self.content_text)
        self.layout = meta['layout']
        self.title = meta['title']
        self.date = self.get_date(meta, self.input_path)
        self.url = self.get_url(meta, config['FN_POST_URL'])
        self.output_path = self.get_output_path(config['DIR_PUBLISH'])
        self.make_excerpt(config['EXCERPT_SEPARATOR'])
        if not self.is_current():
            self.generate_html(pandoc)
        self.wordcount = pandoc.countwords(self.input_path)
        self.topics = ('topics' in meta and meta['topics'].split(" ")) or []

    def get_date(self, meta, input_path):
        pagedate = None
        try:
            pagedate = datetime.date.fromisoformat(str(meta['date']))
        except:
            pass
        if pagedate is None:
            try:
                pagedate = datetime.date.fromisoformat(str(self.input_path.stem[:10]))
            except:
                pass
        if pagedate is None:
            pagedate = datetime.date.today()
        return pagedate

    def get_url(self, meta, urlfn):
        return meta['path']

    def get_output_path(self, site_path):
        path = self.url
        if path.startswith("/"):
            path = path[1:]
        if path.endswith("/"):
            path += "index.html"
        return site_path / pathlib.Path(path)

    def make_excerpt(self, excerpt_sep):
        splittext = self.content_text.split(excerpt_sep, maxsplit=1)
        if len(splittext) == 2:
            self.excerpt_text = splittext[0]
            self.content_text = splittext[1]

    def generate_html(self, pandoc):
        self.content_html = pandoc.markup(input=self.content_text)
        if self.excerpt_text is not None:
            self.excerpt_html = pandoc.markup(input=self.excerpt_text)

    def is_current(self):
        if self.output_path is None or not self.output_path.exists():
            return False
        if self.input_path.stat().st_mtime >= self.output_path.stat().st_mtime:
            return False
        else:
            return True

    def write(self, jinja_env, site_meta):
        if not self.is_current():
            print("Writing:", self)
            template = jinja_env.get_template("{}.html".format(self.layout))
            page = self.get_page_metadata()
            template_out = template.render(content=self.content_html, page=page, post=self, site=site_meta)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(template_out)

    def get_page_metadata(self):
        page = {
            'title': self.title,
            'excerpt': (hasattr(self, 'excerpt_html') and self.excerpt_html) or '',
            'url': self.url
        }
        return page
