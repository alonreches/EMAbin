from WikiSolver import *
from selenium import webdriver
import time
start_xpath = "/html/body/app-root/app-group/div/div/div/div[1]/div/div[1]/div/div/div[2]/div/div/div[2]"
goal_xpath = "/html/body/app-root/app-group/div/div/div/div[1]/div/div[1]/div/div/div[3]/div/div/div[2]"
login_name_xpath = "/html/body/app-root/app-landing-page/div/div/div[2]/div[1]/div/div/form/input"
go_button_xpath = "/html/body/app-root/app-landing-page/div/div/div[2]/div[1]/div/div/form/button"
main_page_timer = '//*[@id="playNowButton"]/small'
game_timer = '/html/body/app-root/app-group/div/div/div[1]/div[1]/div/div[4]'
play_now_button = '//*[@id="playNowButton"]'
# DB_PATH = r'C:\Users\alon\Desktop\HUJI\3rdYear\AI\Project\sdow.sqlite'
driver = webdriver.Chrome()
driver.implicitly_wait(5)
driver.get("https://thewikigame.com")
login_form = driver.find_element_by_xpath(login_name_xpath)
login_form.send_keys("EMA BIN\n")
time.sleep(5)

# db_connection = sqlite3.connect(DB_PATH)
# def list_redirections(page_name):
#     cursor = db_connection.cursor()
#     cursor.execute("select id from pages where title = \"{name}\"".format(name=page_name.replace(" ", "_")))
#     pageid = cursor.fetchall()
#
#     "select * from redirects where target_id = 16881;"

while True:
    try:
        driver.get("https://thewikigame.com/group")
        time_left = int(driver.find_element_by_xpath(main_page_timer).text[:-1])
        while time_left < 100:
            time.sleep(1)
            try:
                time_left = int(driver.find_element_by_xpath(main_page_timer).text[:-1])
            except:
                print("failed to retrieve timer")
                time.sleep(0.5)

        start_article = driver.find_element_by_xpath(start_xpath).text
        goal_article = driver.find_element_by_xpath(goal_xpath).text
        print("loading run")
        fpath, bpath, fopen, bopen, total_time, path_length = run(start=start_article, end=goal_article, algo=bidirectional_a_star,
                                                     forward_heu=splitter_rank_heuristic, backward_heu=merger_rank_heuristic)

        if int(driver.find_element_by_xpath(main_page_timer).text[:-1]) > 15:
            driver.find_element_by_xpath(play_now_button).click()
            time.sleep(2)
            print("PLAYING!")
            path = fpath + bpath[1:]
            print(path)
            for article in path[1:]:
                article = "https://thewikigame.com/wiki/"+article.replace(" ", "_").lower()
                links = driver.find_elements_by_tag_name("a")
                # print([a.get_attribute("href") for a in links])
                for a in links:
                    ref = a.get_attribute("href")
                    if ref is not None and article == ref.lower():
                        print("clicking", ref)
                        a.click()
                        time.sleep(1)
                        break
                else:
                    raise Exception("failed to find %s" % article)
    except:
        import traceback
        traceback.print_exc()
    time.sleep(1)