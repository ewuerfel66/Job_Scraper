class Source:
    def __init__(self, name, codename, home_page):
        self.name = name
        self.codename = codename
        self.home_page = home_page

    def __str__(self):
        return f"{self.name}"