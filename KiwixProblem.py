from bs4 import BeautifulSoup as bs
import requests

BASE_URL = "http://127.0.0.1:8080/wikipedia_en_all_nopic_2017-08/A/"


class wikipage():
    def __init__(self, http_response):
        soup = bs(http_response.content, 'lxml')
        self.links = [a.get('href') for a in soup.find_all('a', href=True) if not a.get('href').startswith("http")]
        self.path = http_response.url[len(BASE_URL):-5:]
        self.title = self.path.replace("_", " ").lower()

    def __eq__(self, other):
        return other.title.lower() == self.title.lower()

    def get_successors(self):
        successors = [wikipedia.page(x) for x in self.links]
        return [x for x in successors if x is not None]


class wikipedia:
    @staticmethod
    def page(name):
        if isinstance(name, str):
            if not name:
                return
            name = name.replace(" ", "_")
            name += ".html" if not name.endswith(".html") else ""
            return wikipage(requests.get(BASE_URL + name))
        if isinstance(name, wikipage):
            return wikipedia.page(name.path)


class WikiProblem:
    def __init__(self, start_state, goal_state):
        self.start_state = wikipedia.page(start_state)
        self.goal_state = wikipedia.page(goal_state)

    def get_start_state(self):
        return self.start_state

    def get_goal_state(self):
        return self.goal_state

    def is_goal_state(self, article):
        return article == self.goal_state

    def get_successors(self, article):
        return article.get_successors()

    def get_predecessor(self):
        raise Exception("Not Implemented! how to find this?")

    def get_categories_of_article(self, article):
        raise Exception("with zim files it might not be possible")
