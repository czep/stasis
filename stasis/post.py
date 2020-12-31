import pathlib

import frontmatter

from .basepage import BasePage

class Post(BasePage):
    def __init__(self, input_path, is_draft=False):
        super().__init__(input_path)
        self.next_post = None
        self.prev_post = None
        self.is_draft = is_draft

    def get_url(self, meta, urlfn):
        args = {
            'meta': meta,
            'input_path': self.input_path
        }
        return urlfn(args)

    def __str__(self):
        if self.date:
            return "Post on {}: {}".format(self.date.isoformat(), self.title)
        else:
            return "Post: {}".format(self.title)

