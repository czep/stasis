import subprocess
import os
import pathlib


class Pandoc():
    def __init__(self, config):
        self.env = {
            **os.environ,
            "LINK_PREFIX": config['SITE']['base_url'],
        }
        self.filters_path = pathlib.Path(__file__).parent.resolve()
        self.fixlinks = "{}/filters/fixlinks.lua".format(str(self.filters_path))
        self.wordcount = "{}/filters/wordcount.lua".format(str(self.filters_path))
        self.args = config['PANDOC_ARGS']

    def markup(self, input):
        encoded_input = input.encode('utf-8')
        cmd = [
            "pandoc",
            "--from", self.args,
            "--to", "html",
            "--lua-filter={}".format(self.fixlinks)
        ]

        res = subprocess.run(cmd, input=encoded_input, capture_output=True, env=self.env)
        return res.stdout.decode('utf-8')

    def countwords(self, infile):
        lua_filter = "{}/filters/wordcount.lua".format(str(pathlib.Path(__file__).parent.resolve()))
        cmd = ["pandoc", "--lua-filter", lua_filter, infile]
        res = subprocess.run(cmd, stdout=subprocess.PIPE)
        wordcount = int(res.stdout.decode('utf-8'))
        return wordcount
