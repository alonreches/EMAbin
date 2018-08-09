##################################################################################
# this module implements the OfflineWikiProblem which serves the problem interface
# using an offline DB that can be downloaded from:
# https://drive.google.com/open?id=1kf_FEVSy6z_ACcL7kqop9a6LCXAP8jKB
##################################################################################
import sqlite3
import os


# static SQL assistance #
# pad a word with spaces and trim it so it will fit to a fixed width table cell.
def trim_len(word, length):
    word = str(word) + ' ' * length
    return word[:length]


# debug function, print the results of a query, pick how many rows you wish to see
def printQ(cursor, query, rownum, row_len):
    cursor.execute(query)
    print('----------------------------')

    colnames = cursor.description
    for element in colnames:
        print(trim_len(element[0], row_len), end="|")
    print()

    print('----------------------------')
    for row in cursor.fetchmany(rownum):
        for element in row:
            print(trim_len(element, row_len), end='|')
        print('\n', end="")

    print('-----------DONE--------------')


# read query result from "pages" table and load them to article-objects list
def pull_articles(cursor, query, rownum=1):
    cursor.execute(query)
    result = []
    if rownum:
        rows = cursor.fetchmany(rownum)
    else:
        rows = cursor.fetchall()

    for row in rows:
        result += [OfflineArticle(row)]
    return result


# read general query results and load them as 2D list
def pull_rows(cursor, query, rownum=1):
    cursor.execute(query)
    result = []
    if rownum:
        rows = cursor.fetchmany(rownum)
    else:
        rows = cursor.fetchall()

    for row in rows:
        result += [list(row)]
    return result


DB_PATH = os.path.join("..", 'sdow.sqlite')


# encapsulate Article object. keep its id and make a nice & simple print
class OfflineArticle:
    def __init__(self, row_from_db):
        self.id = row_from_db[0]
        self.title = row_from_db[1]
        self.is_redirection = row_from_db[2]

    def __str__(self):
        return self.title.replace("_", " ")

    def __repr__(self):
        return self.title.replace("_", " ")

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(int(self.id))


# support A* API
class OfflineWikiProblem:
    def __init__(self, start_state, goal_state):
        self.get_successors_count = 0
        self.get_predecessors_count = 0
        self.db_connection = sqlite3.connect(DB_PATH)
        self.cursor = self.db_connection.cursor()
        self.is_db = True

        src0 = "select * from pages where title = '" + start_state.replace(" ", "_") + "' "
        dest0 = "select * from pages where title = '" + goal_state.replace(" ", "_") + "' "

        self.start_state = pull_articles(self.cursor, src0)
        self.goal_state = pull_articles(self.cursor, dest0)

        if not self.start_state:
            raise Exception('start article is not on the db')

        if not self.goal_state:
            raise Exception('goal article is not on the db')

        self.start_state = self.start_state[0]
        self.goal_state = self.goal_state[0]

    def get_start_state(self):
        return self.start_state

    def get_goal_state(self):
        return self.goal_state

    def is_goal_state(self, article):
        if not self.is_db:
            raise Exception('db is off')

        if article.id == self.goal_state.id:
            self.is_db = False
            self.cursor.close()
            self.db_connection.close()
            return True
        else:
            return False

    # we may need to update this to include redirections as well
    def get_successors(self, article):
        self.get_successors_count += 1
        if not self.is_db:
            raise Exception('db is off')

        query = "select id, outgoing_links from links where id = " + str(article.id)
        # printQ(self.cursor, query,20,20)
        linked_ids = pull_rows(self.cursor, query)[0][1]
        linked_ids = "(" + linked_ids.replace("|", ",") + ")"

        query = "select * from pages where id in " + linked_ids
        # printQ(self.cursor, query, 20, 20)
        return pull_articles(self.cursor, query, 0)

    def get_predecessors(self, article):
        self.get_predecessors_count += 1
        if not self.is_db:
            raise Exception('db is off')

        query = "select id, incoming_links from links where id = " + str(article.id)
        # printQ(self.cursor, query,20,20)
        linked_ids = pull_rows(self.cursor, query)[0][1]
        linked_ids = "(" + linked_ids.replace("|", ",") + ")"

        query = "select * from pages where id in " + linked_ids
        # printQ(self.cursor, query, 20, 20)
        return pull_articles(self.cursor, query, 0)

    def get_categories_of_article(self, article):
        raise Exception("Not Implemented! how to find this?")

    def splitter_rank(self, article):
        out_linkes_count = \
            pull_rows(self.cursor, "select outgoing_links_count from links where id = " + str(article.id))[0][0]
        return out_linkes_count

    def merger_rank(self, article):
        out_linkes_count = \
            pull_rows(self.cursor, "select incoming_links_count from links where id = " + str(article.id))[0][0]
        return out_linkes_count

    def select_name_by_id(self, id_list):
        printQ(self.cursor, 'select * from pages where id in (' + id_list + ')', 200, 30)

    def select_id_by_name(self, names_list):
        printQ(self.cursor, 'select * from pages where title in (' + names_list + ')', 200, 20)

    def select_general_query(self, query):
        printQ(self.cursor, query, 20, 20)


# debug test
def sql_test():
    src_article = "Abraham_Lincoln"
    dest_article = "Autism"

    OWG = OfflineWikiProblem(src_article, dest_article)
    print('src, dest :', OWG.start_state, OWG.goal_state)
    print('src splitter_rank=', OWG.splitter_rank(OWG.start_state))
    print('dest merger_rank=', OWG.merger_rank(OWG.goal_state))

    # printQ(OWG.cursor, 'select * from pages where title in ("Abraham_Lincoln", "Autism")', 7, 25)


    succs = OWG.get_successors(OWG.start_state)
    print("successors:")
    print(succs)

    pred = OWG.get_predecessor(OWG.start_state)
    print("predecessor:")
    print(pred)


def sql_explore():
    src_article = "Abraham_Lincoln"
    dest_article = "Autism"
    OWG = OfflineWikiProblem(src_article, dest_article)
    printQ(OWG.cursor,
           "select * from links where outgoing_links_count between 10 and 20 and  incoming_links_count between 10 and 20 ",
           100, 25)
    OWG.select_name_by_id(
        "7449,7598,10478,13665,18728,23661,24182,32717,39719,40911,40919,41449,41455,41482,41719,41810,42683,42877,43232,44853,44855,44869,47106,47514,49669,51844,53555,53893,55502,55517,58552,60962,60994,66258,66267,68381,68544,68570,69148,70765,70933,71091,72550,74527,75271,76233,77541,77731,77957,78156,78755,79344,79868,80594,83179,83771,84647,84682,87332,92015,94833,95919,96396,105800,118591,141470,141597,142521,143687,143711,144270,144273,144485,144510,145734,146841,147485,147550,149478,152551,152983,153241,156878,159106,163060,171101,173205,173392,177540,178727,179373,182003,183501,186050,186963,188550,189618,191937,192165,193598")

    printQ(OWG.cursor,
           "select avg(incoming_links_count), min(incoming_links_count), max(incoming_links_count) , avg(outgoing_links_count), min(outgoing_links_count), max(outgoing_links_count) from links ",
           50, 25)
