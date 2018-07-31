# TODO: don't make it look like yoni's solution
from WikiProblem import WikiProblem
import util
from sql_offline_queries import *


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


def a_star_search(problem, heuristic=null_heuristic):
    generator = graph_search(problem,
                             util.PriorityQueueWithFunction(lambda node: node.depth + heuristic(node.state, problem)))
    return next(generator)


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
    print("successors_count", problem_forward.get_successors_count)
    print("predecessors_count", problem_backward.get_predecessors_count)
    return forward_intersection.node_path() + back_path[1::]


########################################### NMP^ ########################

def Meta_Data_heuristic(state, problem=None):
    curr_cats = problem.get_categories_of_article(state)
    target_cats = problem.get_categories_of_article(problem.get_goal_state())
    intersection = list(set(curr_cats) & set(target_cats))
    shared = len(intersection)
    f = -(10 ** shared)
    if shared == 0:
        return 0
    if DEBUG:
        print("--------------------------")
        print("now on", state, "with categories: ", curr_cats)
        print("end is", problem.get_goal_state(), "with categories: ", target_cats)
        print("intersection", intersection, "shared", len(intersection))
        print("returned f(x) = ", f)

    return f


def splitter_rank_heuristic(state, problem=None):
    numerator = 1 if state.parent is None else problem.splitter_rank(state.parent.state)
    denominator = problem.splitter_rank(state.state)
    if denominator == 0 or denominator > 500:
        return 500000 #TODO: deal with it correctly
    # print("splitter - numerator", numerator, "denominator", denominator)
    if state.parent is not None:
        print(" --> ".join([x.state.title for x in state.node_path()]))
    return numerator / denominator


def merger_rank_heuristic(state, problem=None):
    numerator = 1 if state.parent is None else problem.merger_rank(state.parent.state)
    denominator = problem.merger_rank(state.state)
    if denominator == 0 or denominator > 800:
        return 500000 #TODO: deal with it correctly
    # print("merger - numerator", state, numerator, "denominator", denominator, "depth", state.depth)
    if state.parent is not None:
        print(" <-- ".join([x.state.title for x in state.node_path()]))
    return numerator / denominator


from sys import argv

DEBUG = False
if len(argv) > 1 and argv[1] == "debug":
    DEBUG = True

START = "Lion Express"
END = "Phinney"


if __name__ == "__main__":
    problem_forward = OfflineWikiProblem(START, END)
    problem_backward = OfflineWikiProblem(END, START)
    print(bidirectional_a_star(problem_forward=problem_forward,
                               problem_backward=problem_backward,
                               heuristic_forward=splitter_rank_heuristic,
                               heuristic_backward=merger_rank_heuristic))

    # print(bidirectional_a_star(problem_forward=problem_forward,
    #                            problem_backward=problem_backward,
    #                            heuristic_forward=lambda n, p: n.depth,
    #                            heuristic_backward=lambda n, p: n.depth))

    # print(a_star_search(problem=problem_forward))

    # print(a_star_search(problem=problem, heuristic=HEURISTIC))
    # problem = OfflineWikiProblem(START, END)
    # print(bfs(problem))
