#######################################################################
# this module implements all solving mechanisms
# it includes a node class (used for tracking depth and path of search)
# a "base search" that is used for running all A* variations
# and all heuristics used in our project
#######################################################################

import os
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial import distance
import json
import wikipedia
from WikiProblem import WikiProblem
import util
from sql_offline_queries import OfflineWikiProblem
import time
from executor import DEBUG
import random
INF = 5000000
INCOMING_LINKS_THRESH = 800
OUTGOING_LINKS_THRESH = 500


class Node:
    """
    node class wrapping the articles. it is needed for tracking depth and path of states
    """
    def __init__(self, article, parent=None, backwards=False):
        self.backwards = backwards
        self.article = article
        self.parent = parent
        self.depth = 0 if parent is None else parent.depth + 1

    def __repr__(self):
        return '<Article: %s>' % (self.article.title,)

    def __hash__(self):
        return hash(self.article)

    def __eq__(self, other):
        return other.article == self.article

    def __str__(self):
        return self.__repr__()

    def get_path(self):
        x, result = self, [self]
        while x.parent is not None:
            result.append(x.parent)
            x = x.parent
        result.reverse()
        return result

    def open_node(self, problem):
        if self.backwards:
            return [Node(next, parent=self, backwards=self.backwards) for next in problem.get_predecessors(self.article)]
        return [Node(next, parent=self, backwards=self.backwards) for next in problem.get_successors(self.article)]


def base_search(problem, fringe, generator=False, backwards=False):
    """
    basic search algorithm to run bfs and A* variations
    """
    fringe.push(Node(problem.get_start_state(), backwards=backwards))
    seen = set()
    while not fringe.isEmpty():
        if generator:
            yield fringe
        node = fringe.pop()
        if DEBUG:
            print("popped:", node.article.title, "parent:", node.parent)
        if problem.is_goal_state(node.article):
            return node.get_path()

        if node.article not in seen:
            seen.add(node.article)
            next_nodes = node.open_node(problem)
            for next_node in next_nodes:
                fringe.push(next_node)
    return


def null_heuristic(node, problem=None):
    return 0


def random_heuristic(node, problem=None):
    """
    a random heuristic gives a random score
    """
    return random.random()


def bfs_heuristic(node, problem=None):
    """
    makes the base search run as bfs
    """
    return node.depth


def a_star_search(problem_forward, problem_backward=None, heuristic_forward=null_heuristic,
                  heuristic_backward=None):
    generator = base_search(problem_forward,
                            util.PriorityQueueWithFunction(lambda node: node.depth + heuristic_forward(node.article,
                                                                                                        problem_forward)))
    path = next(generator)
    return path, [], problem_forward.get_successors_count, -1


def bidirectional_a_star(problem_forward, problem_backward, heuristic_forward=null_heuristic,
                         heuristic_backward=null_heuristic):
    """
    this function run A* in two directions. start to end and end to start.
    every every iteration it compares the nodes in the fringes, and if an intersection is
    found the function calculates the path
    :param problem_forward: problem running start->end
    :param problem_backward: problem running end->start
    :param heuristic_forward: heuristic to use in forward search
    :param heuristic_backward: heuristic to use in backward search
    :return:
    """
    forward_generator = base_search(problem_forward,
                                    util.PriorityQueueWithFunction(
                                         lambda node: heuristic_forward(node, problem_forward)),
                                    generator=True,
                                    backwards=False)
    backward_generator = base_search(problem_backward,
                                     util.PriorityQueueWithFunction(
                                          lambda node: heuristic_backward(node, problem_backward)),
                                     generator=True,
                                     backwards=True)
    fringe_backward = next(backward_generator)
    fringe_forward = next(forward_generator)
    intersection = fringe_forward.intersect(fringe_backward)

    while not intersection:
        fringe_backward = next(backward_generator)
        intersection = fringe_forward.intersect(fringe_backward)
        if intersection:
            break
        fringe_forward = next(forward_generator)
        intersection = fringe_forward.intersect(fringe_backward)

    intersecting_node = min(list(intersection), key=lambda x: x.depth)
    forward_intersection = Node(article=0)
    backward_intersection = Node(article=0)
    forward_intersection.depth = INF
    backward_intersection.depth = INF
    for _, node in fringe_forward.heap:
        if node == intersecting_node and node.depth < forward_intersection.depth:
            forward_intersection = node
    for _, node in fringe_backward.heap:
        if node == intersecting_node and node.depth < backward_intersection.depth:
            backward_intersection = node
    back_path = backward_intersection.get_path()
    back_path.reverse()
    if DEBUG:
        print("successors_count", problem_forward.get_successors_count)
        print("predecessors_count", problem_backward.get_predecessors_count)
    return forward_intersection.get_path(), back_path, \
           problem_forward.get_successors_count, problem_backward.get_predecessors_count


def language_heuristic(state, problem=None):
    """
    heuristic giving a score by the number of languages the article appears in.
    """
    num_of_languages = state.article.num_of_language / 10
    parent_num_of_languages = 1 if state.parent is None else state.parent.article.num_of_language / 10
    denominator = num_of_languages
    numerator = parent_num_of_languages

    if denominator == 0 or num_of_languages > 8:
        return INF
    if state.parent is not None and DEBUG:
        print(" --> ".join([x.article.title for x in state.get_path()]))
    return numerator / denominator + state.depth / 10


def _category_filter(category):
    category = category.split(":")[-1].lower()
    if "lacking" in category:
        return False
    if "article" in category:
        return False
    if "wiki" in category:
        return False
    if category.startswith("all"):
        return False
    if "infobox" in category:
        return False
    if "Hidden categories" in category:
        return False
    if category.startswith("redirects"):
        return False
    if category.startswith("pages"):
        return False
    if category.startswith("Use dmy dates"):
        return False
    if category.startswith("Year of"):
        return False
    return True


def metadata_heuristic(state, problem=None):
    """
    a heuristic giving a score according to the similiratiy in catefories between goal
    and current node. it filters out "bad" categories using the _category_filter function
    """
    curr_cats = list(filter(_category_filter, state.article.categories))
    target_cats = problem.get_goal_state().categories
    intersection = list(set(curr_cats) & set(target_cats))
    shared = len(intersection)
    f = -(10 ** shared)
    if shared == 0:
        return state.depth
    return f


def splitter_rank_heuristic(state, problem=None):
    """
    gives a score according the how many outgoing links the node has,
    and what is the improvement compared to the parent
    used in a forward search.
    """
    numerator = 1 if state.parent is None else problem.splitter_rank(state.parent.article)
    denominator = problem.splitter_rank(state.article)
    if denominator == 0 or denominator > OUTGOING_LINKS_THRESH:
        return INF
    if state.parent is not None and DEBUG:
        print(" --> ".join([x.article.title for x in state.get_path()]))
    return numerator / denominator


def merger_rank_heuristic(state, problem=None):
    """
    gives a score according the how many incoming links the node has,
    and what is the improvement compared to the parent
    used in a backward search.
    """
    numerator = 1 if state.parent is None else problem.merger_rank(state.parent.article)
    denominator = problem.merger_rank(state.article)
    if denominator == 0 or denominator > INCOMING_LINKS_THRESH:
        return INF
    if state.parent is not None and DEBUG:
        print(" <-- ".join([x.article.title for x in state.get_path()]))
    return numerator / denominator


def bow_heuristic(state, problem=None):
    """
    bag of words heuristic.
    builds a vector representing the shared vocabulary,
    and calculates euclidean distance
    """
    vectorizer = CountVectorizer()
    goal_text = problem.get_goal_state().get_text()
    current_text = state.article.get_text()
    X = vectorizer.fit_transform([goal_text, current_text])
    dist = distance.euclidean(X[0].toarray(), X[1].toarray())
    return state.depth + dist


class FeaturesHeuristic:
    """
    this class implements the feature heuristic that is explained in the report
    """
    math_and_science = ["arithmetic", "calculus", "combinatorics", "game theory", "geometry ", "graph theory",
                        "group theory", "linear algebra", "mathematical logic", "model theory",
                        "number theory", "optimization", "order theory", "probability", "set theory",
                        "statistics", "topology", "trigonometry", "linear programming", "research",
                        "general relativity", "quantum mechanics", "physics", "string theory", "electromagnetism",
                        "mechanics", "astronomy", "chemistry", "algorithms", "empirical method"]
    geography = ["geography", "urban planning", "south america", "north america", "antarctica", "europe", "australia",
                 "asia", "africa", "climate", "plate tectonics", "caves", "cities", "countries", "demographics",
                 "deserts", "geographical coordinates", "glaciers", "islands", "lakes", "maps", "mountains",
                 "protected areas", "rivers", "tropical cyclones", "volcanoes", "waterfalls"]
    culture = ["arts‎", "education", "entertainment", "humanities", "language‎",
               "literature‎", "sports", "museums", "music", "tourism‎", "clothing‎", "concert dance", "Culinary arts",
               "film", "celebrity", "leonardo_dicaprio", "actor", "theatre"]
    history = ["history", "archaeology", "archive", "art history", "autobiography", "barbarian", "bolsheviks",
               "bronze age", "caesar", "cliometrics", "age of enlightenment", "humanism", "military history",
               "greek historiography", "cold war", "ancient near east", "chariot",
               "classical greece and rome", "former countries", "history of canada", "chinese history",
               "european history", "indian history", "jewish history", "military history", "middle ages",
               "history of science", "history of the arabs", "history of south america", "renaissance",
               "industrial revolution", "world war i", "world war ii", "printing", "mass media", "information age"]
    society = ["agriculture", "criminology", "economics", "feminism", "gender", "health", "immigration",
               "social inequality", "law", "politics", "ethnic group", "social movements", "democracy", "peace",
               "property", "revolution", "rights", "social contract", "war", "media (communication)", "transport",
               "leisure", "industry", "sex"]
    religion = ["religion", "christianity", "judaism", "hinduism", "bahá'í faith", "islam", "taoism", "confucianism",
                "shinto", "buddhism", "sikh", "fasting", "festivals", "holy days", "idolatry", "mysticism",
                "prayer", "rituals", "scientology", "angels", "demons", "polytheism", "mythology",
                "religion and lgbt people", "sexuality and religion", "theology", "marriage", "atheism", "spiritualism"]
    biology_anatomy = ["List of systems of the human body", "Bone", "Muscle", "Vein", "Heart", "Brain", "Skin",
                       "Kidney", "Life", "species", "biology", "Evolution", "mutation", "mammal", "animal", "DNA",
                       "RNA", "protein", "enzyme", "protein folding", "carbohydrate", "lipid", "glycolysis",
                       "citric acid cycle", "electron transport chain", "oxidative phosphorylation", "photosynthesis",
                       "protein structure", "genome", "chromosome", "cell (biology)", "food chain", "extinction",
                       "health", "death", "medicine", "medication", "life expectancy"]
    technology = ["industry", "innovation", "technocapitalism", "technological evolution", "automobile", "big science",
                  "biotechnology", "communication", "design", "electronics", "energy development", "engineering",
                  "food science", "industry", "internet", "machines", "management", "manufacturing",
                  "mass communication", "mass production", "nanotechnology", "nuclear technology", "processes",
                  "robotics", "space exploration", "technology forecasting", "weapons", "information systems",
                  "programming", "artificial intelligence"]

    features = [math_and_science, geography, culture, history, society, religion, biology_anatomy, technology]
    features_names = ["math_and_science", "geography", "culture", "history", "society", "religion", "biology_anatomy",
                      "technology"]

    def __init__(self):
        self.all_texts = {}
        self.vectorizer = None
        self._text_loader()
        self.vocabulary = self._build_vocabulary()
        self.goal_vec = None

    def _build_vocabulary(self):
        words = set()
        for text in self.all_texts.values():
            spilt_text = set(text.split())
            words = words.union(spilt_text)
        return list(words)

    @staticmethod
    def _scraper():
        import json
        for i in range(5, len(FeaturesHeuristic.features)):
            texts_dict = {}
            for feature in FeaturesHeuristic.features[i]:
                texts_dict[feature] = wikipedia.page(feature).content
            texts_json = json.dumps(texts_dict)
            f = open(os.path.join("feature_articles", FeaturesHeuristic.features_names[i] + "_feature_texts.json"), 'w')
            f.write(texts_json)
            f.close()

    def _text_loader(self):
        if len(self.all_texts) == 0:
            for i in range(len(self.features)):
                f = open(os.path.join("feature_articles", FeaturesHeuristic.features_names[i] + "_feature_texts.json"),
                         'r')
                self.all_texts.update(json.load(f))

    def _article_to_vec(self, article):
        article_text = article.content
        vec = []
        for cord in self.features:
            scores = []
            for feature in cord:
                scores.append(self._get_score(article_text, self.all_texts[feature]))
            # vec.append(sum(scores) / len(scores))
            vec.append(min(scores))
        sum_vec = sum(vec)
        if sum_vec != 0 and DEBUG:
            print_vec = [cord / sum_vec for cord in vec]
            for i in range(len(print_vec)):
                print(self.features_names[i] + ": " + str(print_vec[i]))
        return vec if sum_vec == 0 else [cord / sum_vec for cord in vec]

    def _get_score(self, article_text, feature_text):
        if self.vectorizer is None:
            self.vectorizer = CountVectorizer(vocabulary=self.vocabulary)
        bags_of_words = self.vectorizer.fit_transform([article_text, feature_text])
        return distance.euclidean(bags_of_words[0].toarray(), bags_of_words[1].toarray())

    def features_heuristic(self, node, problem=None):
        if self.goal_vec is None:
            self.goal_vec = self._article_to_vec(problem.get_goal_state())
        state_vec = self._article_to_vec(node.article)
        dist = distance.euclidean(state_vec, self.goal_vec)
        return node.depth + dist


def run(start, end, algo, forward_heu, backward_heu):
    """
    execution function. this function allows the user to run any combination of algorithm and heuristic
    in the same manner
    :param start: name of start article
    :param end: name of goal article
    :param algo: search algorithm to use
    :param forward_heu: heuristic for forward search
    :param backward_heu: heuristic for backward search
    :return:
    """
    offline_heuristics = (bfs_heuristic, merger_rank_heuristic, splitter_rank_heuristic, random_heuristic)

    if forward_heu in offline_heuristics:
        problem_forward = OfflineWikiProblem(start, end)
    else:
        problem_forward = WikiProblem(start, end)

    if backward_heu in offline_heuristics:
        problem_backward = OfflineWikiProblem(end, start)
    else:
        problem_backward = WikiProblem(end, start)

    start = time.time()
    fpath, bpath, fopen, bopen = algo(problem_forward=problem_forward,
                                      problem_backward=problem_backward,
                                      heuristic_forward=forward_heu,
                                      heuristic_backward=backward_heu)
    total_time = time.time() - start
    return [x.article.title for x in fpath], [x.article.title for x in bpath], fopen, bopen, total_time, len(fpath) + len(
        bpath) - 1