import sqlite3

def trim_len(word, length):
    word = str(word)+' '*length
    return word[:length]

def printQ(cursor,query,rownum, row_len):
    cursor.execute(query)
    print('----------------------------')

    colnames = cursor.description
    for element in colnames:
        print(trim_len(element[0],row_len), end="|")
    print()


    print('----------------------------')
    for row in cursor.fetchmany(rownum):
        for element in row:
            print(trim_len(element,row_len), end='|')
        print('\n', end="")

    print('-----------DONE--------------')

def pull_rows(cursor,query,rownum = 1):
    cursor.execute(query)
    result = []
    if rownum:
        rows = cursor.fetchmany(rownum)
    else:
        rows = cursor.fetchall()

    for row in rows:
        result += [list(row)]
    return result


DB_PATH = r'W:\CS\AI\final project\sdow.sqlite.db'

##############################################################################################
'''conn = sqlite3.connect(DB_PATH)
c = conn.cursor()


rdirect = c.execute(r"select * from redirects ")
#printQ(c, 7, 15)

links = c.execute(r"select * from links ")
#printQ(c, 7, 15)


src_article = "Abraham_Lincoln"
dest_article = "Autism"

src0 = "select id from pages where title = '"+src_article+"' "
dest0 = "select id from pages where title = '"+dest_article+"' "

quer = src0
#printQ(c,quer, 7, 15)

assist = "select id, outgoing_links from links natural join ("+src0+")"
assist = "select links.id, outgoing_links, pages.id from links left join pages on links.outgoing_links like pages.id"
#assist = 'select * from pages where id in (25,39,290,307)'
#assist = "select id from pages where id in()"
printQ(c,assist, 7, 20)
'''
##################################################################################################
def printArticles(ArtList):
    for a in ArtList:
        print(a[1])


class OfflineWikiProblem:
    def __init__(self, start_state, goal_state):
        self.db_connection = sqlite3.connect(DB_PATH)
        self.cursor = self.db_connection.cursor()
        self.is_db = True

        src0 = "select * from pages where title = '" + start_state + "' "
        dest0 = "select * from pages where title = '" + goal_state + "' "

        self.start_state = pull_rows(self.cursor, src0)[0]
        self.goal_state = pull_rows(self.cursor, dest0)[0]

    def get_start_state(self):
        return self.start_state

    def get_goal_state(self):
        return self.goal_state

    def is_goal_state(self, article):
        if not self.is_db:
            raise Exception('db is off')

        if article[0] == self.goal_state[0]:
            self.is_db == False
            self.cursor.close()
            self.db_connection.close()
            return True
        else:
            return False

    def get_successors(self, article):
        if not self.is_db:
            raise Exception('db is off')

        query = "select id, outgoing_links from links where id = "+str(article[0])
        #printQ(self.cursor, query,20,20)
        linked_ids = pull_rows(self.cursor, query)[0][1]
        linked_ids = "(" + linked_ids.replace("|", ",") + ")"

        query = "select * from pages where id in "+linked_ids
        #printQ(self.cursor, query, 20, 20)
        return pull_rows(self.cursor, query, 0)


    def get_predecessor(self, article):
        if not self.is_db:
            raise Exception('db is off')

        query = "select id, incoming_links from links where id = "+str(article[0])
        #printQ(self.cursor, query,20,20)
        linked_ids = pull_rows(self.cursor, query)[0][1]
        linked_ids = "(" + linked_ids.replace("|", ",") + ")"

        query = "select * from pages where id in "+linked_ids
        #printQ(self.cursor, query, 20, 20)
        return pull_rows(self.cursor, query, 0)

    def get_categories_of_article(self, article):
        raise Exception("Not Implemented! how to find this?")

    def run_dfs(self):
        raise Exception("Not Implemented yet!")


src_article = "Abraham_Lincoln"
dest_article = "Autism"

OWG = OfflineWikiProblem(src_article, dest_article)
print('src, dest :',OWG.start_state,OWG.goal_state)

succs = OWG.get_successors(OWG.start_state)
print ("successors:")
printArticles(succs)

pred = OWG.get_predecessor(OWG.start_state)
print ("predecessor:")
printArticles(pred)
