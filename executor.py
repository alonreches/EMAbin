from improved_wikipedia import wikipedia
import random
import itertools
from WikiSolver import *

POPULAR_PAGES_ID = "37397829"
from sys import argv

DEBUG = False
if len(argv) > 1 and argv[1] == "debug":
    DEBUG = True


def generate_popular_pages():
    popular_pages = wikipedia.page(pageid=POPULAR_PAGES_ID)
    popular_links = popular_pages.links
    # Generate all possible non-repeating pairs
    pairs = list(itertools.combinations(popular_links, 2))
    # print(popular_pages.title)
    while True:
        # Randomly choose pair of links
        yield random.choice(pairs)

def parse_run(start_art, end_art, algo, forward, backward):
    fpath, bpath, fopen, bopen, total_time, depth = run(start_art, end_art, algo, forward, backward)
    print("  ", depth," -> ".join(fpath)," | "," -> ".join(bpath), )
    print("  opened from start:",fopen, "opened from end:", bopen)
    print("  took: ", round(total_time/60,2), "mins")
    return " -> ".join(fpath)+" | "+" -> ".join(bpath), bopen,fopen,round(total_time/60,2),depth


def short_test_heuristic(algo, forward, backward=None):
    print('--------now testing heuristic', algo.__name__, 'with', forward.__name__, "and", backward.__name__, 'shortly -------------------')
    print('genre: impulsive choice')
    generator = generate_popular_pages()
    for i in range(5):
        start_art, end_art = next(generator)
        print('  run from %s to %s...' % (start_art, end_art))
        parse_run(start_art, end_art, algo, forward, backward )

    print('genre: hierarchy tasks')

    start_art, end_art = "Quark", "Marble"
    print('  run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Marble", "Quark"
    print('  and backwards: run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Slender-snouted_crocodile", "Flatworm"
    print('  run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Flatworm", "Slender-snouted_crocodile"
    print('  and backwards: run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    start_art, end_art = "Ossicles", "Glomerulus_(kidney)"
    print('  path between edges : run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

    print('genre: extreme tasks')
    start_art, end_art = "Ossicles", "Glomerulus_(kidney)"
    print('  path between edges : run from %s to %s...' % (start_art, end_art))
    print('  ', parse_run(start_art, end_art, algo, forward, backward))

def extreme_test_heuristic(samples,algo, forward, backward=None, ):
    print('--------now testing heuristic', algo.__name__, 'with', forward.__name__, "and", backward.__name__,
          'overnight -------------------')
    generator = generate_popular_pages()
    file = open("extreme_test_results.txt", 'w', 1)
    file.write('genre\tdepth\theu-path\topened-src\topend-dest\theu-opened-total\ttime\tbfs_depth\tbfs_path\tbfs-opened-total\n')

    for i in range(samples):
        try:
            start_art, end_art = next(generator)
            print('  run from %s to %s...' % (start_art, end_art))
            heu = parse_run(start_art, end_art, algo, forward, backward)
            bfs = parse_run(start_art, end_art, algo, lambda n, p: n.depth, lambda n, p: n.depth)
            file.write('\t'.join(['impulsive choice',str(heu[4]),str(heu[0]),str(heu[2]),str(heu[1]),str(int(bfs[1])+int(bfs[2])),str(heu[3]),str(bfs[0]),str(bfs[4]),str(int(bfs[1])+int(bfs[2]))])+'\n')

        except:
            continue

    for i in range(samples):
        try:
            start_art, end_art = wikipedia.random(),wikipedia.random()
            print('  run from %s to %s...' % (start_art, end_art))
            heu = parse_run(start_art, end_art, algo, forward, backward)
            bfs = parse_run(start_art, end_art, algo, lambda n, p: n.depth, lambda n, p: n.depth)
            file.write('\t'.join(['uniform choice',str(heu[4]),str(heu[0]),str(heu[2]),str(heu[1]),str(heu[3]),str(bfs[0]),str(bfs[4]),str(int(bfs[1])+int(bfs[2]))])+'\n')

        except:
            continue
    file.close()






if __name__ == "__main__":
    #short_test_heuristic(bidirectional_a_star, splitter_rank_heuristic, merger_rank_heuristic)
    extreme_test_heuristic(10, bidirectional_a_star, splitter_rank_heuristic, merger_rank_heuristic)
    print('DONE')