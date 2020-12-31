from .basepage import BasePage

class Page(BasePage):
    def __init__(self, input_path):
        print("Creating Page from file:", input_path)
        super().__init__(input_path)

    def __str__(self):
        return "Page at {}: {}".format(self.url, self.title)
