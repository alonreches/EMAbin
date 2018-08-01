# TODO: don't make it look like yoni's solution
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial import distance
from optparse import OptionParser
from WikiProblem import WikiProblem
import util
from sql_offline_queries import *
import time
try:
    from executor import DEBUG
except:
    DEBUG = True


class Node:
    def __init__(self, state, parent=None, path_cost=0, backwards=False):
        self.backwards = backwards
        self.state = state
        self.parent = parent
        if parent:
            self.path_cost = parent.path_cost + path_cost
            self.depth = parent.depth + 1
        else:
            self.path_cost = path_cost
            self.depth = 0

    def __repr__(self):
        return '<Node %s>' % (self.state.title,)

    def node_path(self):
        x, result = self, [self]
        while x.parent:
            result.append(x.parent)
            x = x.parent

        result.reverse()
        return result

    def path(self):
        actions = []
        currnode = self
        while currnode.parent:
            actions.append(currnode.action)
            currnode = currnode.parent

        actions.reverse()
        return actions

    def expand(self, problem):
        if self.backwards:
            return [Node(next, parent=self, backwards=self.backwards) for next in problem.get_predecessors(self.state)]
        return [Node(next, parent=self, backwards=self.backwards) for next in problem.get_successors(self.state)]

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return other.state == self.state


REVERSE_PUSH = False


def graph_search(problem, fringe, generator=False, backwards=False):
    start_state = problem.get_start_state()
    fringe.push(Node(problem.get_start_state(), backwards=backwards))
    try:
        start_state.__hash__()
        visited = set()
    except:
        visited = list()

    while not fringe.isEmpty():
        if generator:
            yield fringe
        node = fringe.pop()
        if DEBUG:
            print("popped:", node.state.title, "parent:", node.parent)
        if problem.is_goal_state(node.state):
            return node.node_path()
        try:
            in_visited = node.state in visited
        except:
            visited = list(visited)
            in_visited = node.state in visited

        if not in_visited:
            if isinstance(visited, list):
                visited.append(node.state)
            else:
                visited.add(node.state)
            next_nodes = node.expand(problem)
            if REVERSE_PUSH:
                next_nodes.reverse()
            for next_node in next_nodes:
                fringe.push(next_node)
    return


def null_heuristic(state, problem=None):
    return 0


def a_star_search(problem_forward, problem_backward=None, heuristic_forward=null_heuristic,
                         heuristic_backward=None):
    generator = graph_search(problem_forward,
                             util.PriorityQueueWithFunction(lambda node: node.depth + heuristic_forward(node.state,
                                                                                                        problem_forward)))
    path = next(generator)
    return path, [], problem_forward.get_successors_count, -1


def bfs(problem, heuristic=null_heuristic):
    return graph_search(problem, util.Queue())


# TODO: Maybe consider shortcuts found along the way
# TODO: rewrite nicely this function
def bidirectional_a_star(problem_forward, problem_backward, heuristic_forward=null_heuristic,
                         heuristic_backward=null_heuristic):
    forward_generator = graph_search(problem_forward,
                                     util.PriorityQueueWithFunction(
                                         lambda node: heuristic_forward(node, problem_forward)),
                                     generator=True,
                                     backwards=False)
    backward_generator = graph_search(problem_backward,
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
    forward_intersection = Node(state=0)
    backward_intersection = Node(state=0)
    forward_intersection.depth = 500000
    backward_intersection.depth = 500000
    for _, node in fringe_forward.heap:
        if node == intersecting_node and node.depth < forward_intersection.depth:
            forward_intersection = node
    for _, node in fringe_backward.heap:
        if node == intersecting_node and node.depth < backward_intersection.depth:
            backward_intersection = node
    back_path = backward_intersection.node_path()
    back_path.reverse()
    if DEBUG:
        print("successors_count", problem_forward.get_successors_count)
        print("predecessors_count", problem_backward.get_predecessors_count)
    return forward_intersection.node_path(), back_path,\
           problem_forward.get_successors_count, problem_backward.get_predecessors_count


########################################### NMP^ ########################
def language_heuristic(state, problem=None):
    num_of_languages = state.state.num_of_language / 10
    parent_num_of_languages = 1 if state.parent is None else state.parent.state.num_of_language / 10
    denominator = num_of_languages
    numerator = parent_num_of_languages

    if denominator == 0 or num_of_languages > 8:
        return 500000 #TODO: deal with it correctly
    if state.parent is not None and DEBUG:
        print(" --> ".join([x.state.title for x in state.node_path()]))
    return numerator / denominator + state.depth/10


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
    curr_cats = list(filter(_category_filter, state.state.categories))
    target_cats = problem.get_goal_state().categories
    intersection = list(set(curr_cats) & set(target_cats))
    shared = len(intersection)
    f = -(10 ** shared)
    if shared == 0:
        return state.depth
    return f


def splitter_rank_heuristic(state, problem=None):
    numerator = 1 if state.parent is None else problem.splitter_rank(state.parent.state)
    denominator = problem.splitter_rank(state.state)
    if denominator == 0 or denominator > 500:
        return 500000 #TODO: deal with it correctly
    # print("splitter - numerator", numerator, "denominator", denominator)
    if state.parent is not None and DEBUG:
        print(" --> ".join([x.state.title for x in state.node_path()]))
    return numerator / denominator


def merger_rank_heuristic(state, problem=None):
    numerator = 1 if state.parent is None else problem.merger_rank(state.parent.state)
    denominator = problem.merger_rank(state.state)
    if denominator == 0 or denominator > 800:
        return 500000 #TODO: deal with it correctly
    # print("merger - numerator", state, numerator, "denominator", denominator, "depth", state.depth)
    if state.parent is not None and DEBUG:
        print(" <-- ".join([x.state.title for x in state.node_path()]))
    return numerator / denominator


def bow_heuristic(state, problem=None):
    vectorizer = CountVectorizer()
    goal_text = problem.get_goal_state().get_text()
    current_text = state.state.get_text()
    X = vectorizer.fit_transform([goal_text, current_text])
    dist = distance.euclidean(X[0].toarray(), X[1].toarray())
    return state.depth + dist

START = "Charlie Brown"
END = "Null Island"


def run(start, end, algo, forward_heu, backward_heu):
    if forward_heu in (bow_heuristic, language_heuristic, metadata_heuristic):
        problem_forward = WikiProblem(start, end)
        problem_backward = WikiProblem(end, start)
    else:
        problem_forward = OfflineWikiProblem(start, end)
        problem_backward = OfflineWikiProblem(end, start)
    start = time.time()
    fpath, bpath,  fopen, bopen = algo(problem_forward=problem_forward,
                                       problem_backward=problem_backward,
                                       heuristic_forward=forward_heu,
                                       heuristic_backward=backward_heu)
    total_time = time.time() - start
    return [x.state.title for x in fpath], [x.state.title for x in bpath], fopen, bopen, total_time, len(fpath)+len(bpath)-1

if __name__ == "__main__":
    problem_forward = WikiProblem(START, END)
    problem_backward = WikiProblem(END, START)
    print(bidirectional_a_star(problem_forward=problem_forward,
                               problem_backward=problem_backward,
                               heuristic_forward=bow_heuristic,
                               heuristic_backward=bow_heuristic))

    # print(bidirectional_a_star(problem_forward=problem_forward,
    #                            problem_backward=problem_backward,
    #                            heuristic_forward=lambda n, p: n.depth,
    #                            heuristic_backward=lambda n, p: n.depth))

    # print(a_star_search(problem=problem_forward))

    # print(a_star_search(problem=problem, heuristic=HEURISTIC))
    # problem = OfflineWikiProblem(START, END)
    # print(bfs(problem))


# TODO: use this for writing the execution from cmd line
# def main():
#
#     usage = """EMA BIN LOVES YOU"""
#     parser = OptionParser(usage)
#
#     parser.add_option('-s', '--start', dest='start',
#                       help='start article')
#
#     parser.add_option('-e', '--end', dest='end',
#                       help='end article')
#
#     parser.add_option('-db', '--db', dest='db',
#                       help='from where to get the data',
#                       default='db')
#
#     parser.add_option('-db', '--db', dest='db',
#                       help='from where to get the data',
#                       default='db')
#
#     parser.add_option('-a', '--algorithm', dest='algorithm',
#                       help='algorithm',
#                       default='bidirectional_a_star')
#
#     parser.add_option('-fh', '--forward_heuristic', dest='forward_heuristic',
#                       help='forward heuristic',
#                       default='splitter_rank_heuristic')
#
#     parser.add_option('-bh', '--backward_heuristic', dest='backward_heuristic',
#                       help='backward heuristic',
#                       default='merger_rank_heuristic')
#     options = parser.parse_args()
#
#     forward_heuristic = getattr()
#
#     if options.db == "db":
#         problem = OfflineWikiProblem
#
#     elif options.db == "online":
#         problem = WikiProblem
#
#     if options.algorithm == "bidirectional":
#         algorithm = bidirectional_a_star
#         start_to_end = problem(options.start, options.end)
#         end_to_start = problem(options.end, options.start)
#
#     elif options.algorithm == "a_star":
#         algorithm = a_star_search
#         start_to_end = problem(options.start, options.end)
