# TODO: don't make it look like yoni's solution
from WikiProblem import WikiProblem
import util


class Node:
    def __init__(self, state, parent=None, path_cost=0):
        self.state = state
        self.parent = parent
        if parent:
            self.path_cost = parent.path_cost + path_cost
            self.depth = parent.depth + 1
        else:
            self.path_cost = path_cost
            self.depth = 0

    def __repr__(self):
        return '<Node %s>' % (self.state,)

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
        return [Node(next, parent=self) for next in problem.get_successors(self.state)]


REVERSE_PUSH = False


def graph_search(problem, fringe):
    start_state = problem.get_start_state()
    fringe.push(Node(problem.get_start_state()))
    try:
        start_state.__hash__()
        visited = set()
    except:
        visited = list()

    while not fringe.isEmpty():
        node = fringe.pop()
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
    if state == "Machine" or state == "Engine":
        return 1
    else:
        return 100


def a_star_search(problem, heuristic=null_heuristic):
    return graph_search(problem,
                        util.PriorityQueueWithFunction(lambda node: node.path_cost + heuristic(node.state, problem)))

if __name__ == "__main__":
    problem = WikiProblem("Cowling", "Machine")
    print(a_star_search(problem=problem))
