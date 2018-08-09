###########################################################################
# this module implements the WikiProblem which serves the problem interface
# using the online wikipedia API. it gives more data (text, categories etc.)
# but is slower than the offline interface
###########################################################################
from improved_wikipedia import wikipedia
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup as bs
import requests

WIKIPEDIA_QUERY_LIMIT = 50


class WikiProblem:
    def __init__(self, start_state, goal_state):
        self.get_successors_count = 0
        self.get_predecessors_count = 0
        self.start_state = wikipedia.pages([start_state])[0]
        self.goal_state = wikipedia.pages([goal_state])[0]

    def get_start_state(self):
        return self.start_state

    def get_goal_state(self):
        return self.goal_state

    def is_goal_state(self, article):
        return article == self.goal_state

    def get_successors(self, article):
        self.get_successors_count += 1
        return self._get_pages(self._divide_to_chunks(article.links))

    def get_predecessors(self, article):
        self.get_predecessors_count += 1
        url = 'http://en.wikipedia.org/w/index.php?title=Special%3AWhatLinksHere&limit=500&target=' + article.title + '&namespace=0'
        http_response = requests.get(url)
        soup = bs(http_response.content, 'lxml')
        ul = soup.find_all('ul', id="mw-whatlinkshere-list")
        a_tags = ul[0].find_all('a')
        names = [x.contents[0] for x in a_tags[::3]]
        return self._get_pages(self._divide_to_chunks(names))

    def get_categories_of_article(self, article):
        return article.categories

    def _get_pages(self, links):
        pool = ThreadPool(processes=1)
        threads = []
        wikipages = []
        for chunk in links:
            async_result = pool.apply_async(self._get_chunk_of_pages, (chunk,))
            threads.append(async_result)
        for thread in threads:
            wikipages.extend(thread.get())
        pool.close()
        return wikipages

    def _get_chunk_of_pages(self, article_names):
        pages = wikipedia.pages(article_names)
        # print("\t", "requested:", len(article_names), "got:", len(pages))
        return pages

    @staticmethod
    def _divide_to_chunks(iterable):
        chunks = []
        counter = len(iterable)
        while counter > 0:
            start = max(0, counter - WIKIPEDIA_QUERY_LIMIT)
            chunks.append(iterable[start:counter])
            counter -= WIKIPEDIA_QUERY_LIMIT
        return chunks