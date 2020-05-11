import datetime
import email
import imaplib
from selenium import webdriver
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import multiprocessing


# Sports xpath list
def sports_xpath(sport):
    if sport == "NCAAB" :
        sport_x = "//div[@class='margin-left-10 flex']//div[1]//md-list-item[1]//div[1]//div[1]//div[1]//div[1]//md-checkbox[1]//div[2]//span[1]"
        return sport_x
    elif sport == "NBA" :
        sport_x = "//div[@class='flex']//div[1]//md-list-item[1]//div[1]//div[1]//div[1]//div[1]//md-checkbox[1]//div[2]//span[1]"
        return sport_x


#sports unit list
just_bettor_unit = {"nba":10,"nccab":11}


# team name list (please provide all name as lower case)
Team_list_NBA = {'orlando': 'orlando magic', 'los angeles': 'los angeles lakers', 'boston': 'boston celtics', 'portland': 'portland trail blazers', 'cleveland': 'cleveland cavaliers', 'new orleans': 'new orleans pelicans', 'charlotte': 'charlotte hornets', 'indiana': 'indiana pacers', 'memphis': 'memphis grizzlies', 'sacramento': 'sacramento kings', 'dallas': 'dallas mavericks', 'brooklyn': 'brooklyn nets', 'atlanta': 'atlanta hawks', 'washington': 'washington wizards', 'philadelphia': 'philadelphia 76ers', 'toronto': 'toronto raptors', 'detroit': 'detroit pistons', 'new york': 'new york knicks', 'golden state': 'golden state warriors', 'minnesota': 'minnesota timberwolves', 'utah': 'utah jazz', 'milwaukee': 'milwaukee bucks', 'san antonio': 'san antonio spurs', 'denver': 'denver nuggets', 'chicago': 'chicago bulls', 'houston': 'houston rockets', 'phoenix': 'phoenix suns', 'oklahoma city': 'oklahoma city thunder', 'miami': 'miami heat'}
Team_list_NCCAB = {'cincinnati': 'cincinnati', 'east carolina': 'east carolina', 'st. joes': "st. joseph's", 'nc state': 'nc state', 'florida international': 'fiu', 'illinois-chicago': 'illinois chicago', 'nebraska omaha': 'nebraska omaha', 'purdue fort wayne': 'ipfw', 'ark little rock': 'arkansas little rock'}

# first site
def just_bettor(sport,team1,symbol,unit,main_part):
    # provide units for this site
    unit_value = just_bettor_unit[sport.lower()]
    try:
        driver = webdriver.Chrome('./chromedriver')
        driver.implicitly_wait(10)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'Accept-Encoding': 'gzip,deflate'}
        driver.get("https://just4bettors.eu/")
        # please provide site credentials
        driver.find_element_by_id('customerID').send_keys("")
        driver.find_element_by_id('password').send_keys("")
        driver.find_element_by_xpath("//input[@class='login__input login__input--submit']").click()
        try:
            driver.find_element_by_xpath(
                "//md-list-item[@class='md-1-line sport-list-item md-proxy-focus _md md-clickable']//div//span[contains(text(),'NCAA Basketball')]")
        except:
            # please provide site credentials
            driver.find_element_by_id("loginName").send_keys("")
            driver.find_element_by_id("password").send_keys("")
            driver.find_element_by_xpath("//span[contains(text(),'Login')]").click()
        driver.find_element_by_xpath(sports_xpath(sport)).click()
        driver.find_element_by_xpath(
            "//button[@class='btnContinue md-button md-blue-grey-theme md-ink-ripple']//span[contains(text(),'Continue')]").click()
        SCROLL_PAUSE_TIME = 0.5
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        all_teams = driver.find_elements_by_class_name("game-description.flex")
        a = 0
        c = 0
        d = 0
        full_team_name = None
        if team1 in Team_list_NBA:
                        team1 = Team_list_NBA[team1]
        elif team1 in Team_list_NCCAB:
            team1 = Team_list_NCCAB[team1]
        for all_team in all_teams:
            c += 1
            if team1.lower() in all_team.text.lower():
                a = c
                full_team_name = all_team.text.lower()

        game_times = driver.find_elements_by_class_name("game-time.linked-lines")
        for time_temp in game_times:
            d += 1
            if d == a:
                time_temp.location_once_scrolled_into_view
                driver.execute_script("window.scrollTo(-100, 0);")
                time_temp.click()
        if "vs" in full_team_name:
            full_team_name = full_team_name.split("vs")
        elif:
            full_team_name = full_team_name.split("@")
        game_time = driver.find_element_by_xpath(
            "//div[@class='boxTime margin-right-10 layout-align-center-center layout-column flex-25']").text.replace(
            "\n", " ")
        box_input = driver.find_elements_by_xpath("//input[starts-with(@id,'input_')]")
        input_dict = {}
        temp_number = 1
        for ids in box_input:
            input_dict[temp_number] = ids.get_attribute("id")
            temp_number += 1
        if len(input_dict) < 3:
            input_dict[6] = input_dict[2]
        units = int(unit) * unit_value
        if team1.lower() in full_team_name[0]:
            if symbol == "+":
                driver.find_element_by_id(input_dict[1]).send_keys(units)
            elif symbol == "-":
                driver.find_element_by_id(input_dict[1]).send_keys(units)
            elif symbol.lower() == "o":
                driver.find_element_by_id(input_dict[3]).send_keys(units)
            elif symbol.lower() == "u":
                driver.find_element_by_id(input_dict[8]).send_keys(units)
            time.sleep(2)
            driver.find_element_by_xpath("//div[@class='btnContinue flex-5']").click()
        elif team1.lower() in full_team_name[1]:
            if symbol == "+":
                driver.find_element_by_id(input_dict[6]).send_keys(units)
            elif symbol == "-":
                driver.find_element_by_id(input_dict[6]).send_keys(units)
            elif symbol.lower() == "o":
                driver.find_element_by_id(input_dict[3]).send_keys(units)
            elif symbol.lower() == "u":
                driver.find_element_by_id(input_dict[8]).send_keys(units)
            time.sleep(2)
            driver.find_element_by_xpath("//div[@class='btnContinue flex-5']").click()
        risk = driver.find_element_by_xpath(
            "/html[1]/body[1]/div[1]/div[2]/md-content[1]/div[1]/div[1]/div[2]/ng-switch[1]/div[1]/div[1]/div[1]/md-card[1]/md-list[1]/md-list-item[1]/div[1]/div[1]/div[8]/button[1]").text
        won = driver.find_element_by_xpath(
            "/html[1]/body[1]/div[1]/div[2]/md-content[1]/div[1]/div[1]/div[2]/ng-switch[1]/div[1]/div[1]/div[1]/md-card[1]/md-list[1]/md-list-item[1]/div[1]/div[1]/div[9]/button[1]").text
        # final confirmation
        # driver.find_element_by_xpath("//span[contains(text(),'Confirm')]").click()
        driver.quit()
        end_time = (datetime.datetime.now() - start_time).seconds
        sheet = client.open('completed').sheet1
        date = datetime.date.today().strftime("%d/%m/%Y")
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.insert_row([date, sport, date_time, main_part, risk, won, unit, game_time, end_time], 2)
        error_sheet.delete_row(2)
        time.sleep(1)

    except Exception as error:
        print(error)


scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets',
                         'https://www.googleapis.com/auth/drive.file']
credentials = ServiceAccountCredentials.from_json_keyfile_name('sheets.json', scope)
client = gspread.authorize(credentials)
error_sheet = client.open('error_sheet').sheet1
total_records = error_sheet.get_all_records()
for all_record in range(len(total_records)):
    A = error_sheet.row_values(2)
    if len(A) != 0:
        sport = A[0]
        team1 = A[1]
        symbol = A[2]
        unit= A[3]
        main_part = A[5]
        
        #first site
        just_bettor(sport,team1,symbol,unit,main_part)
