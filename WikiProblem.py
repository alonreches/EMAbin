import wikipedia


class WikiProblem:
    def __init__(self, start_state, goal_state):
        self.start_state = wikipedia.page(start_state)
        self.goal_state = wikipedia.page(goal_state)

    def get_start_state(self):
        return self.start_state.title

    def get_goal_state(self):
        return self.goal_state.title

    def is_goal_state(self, article):
        try:
            a = wikipedia.page(article).title
            b = self.goal_state.title
            return a == b
        except Exception as E:
            return False

    def get_successors(self, article):
        try:
            return wikipedia.page(article).links
        except Exception as E:
            return []

    def get_predecessor(self):
        raise Exception("Not Implemented! how to find this?")

    def get_categories_of_article(self, article):
        return wikipedia.page(article).categories

    def run_dfs(self):
        raise Exception("Not Implemented yet!")
