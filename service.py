from datetime import datetime, timedelta
import json
import requests
from bs4 import BeautifulSoup
import config
from os import path

config = config.DEFAULT
FORMAT = "%Y-%m-%d %H:%M:%S"

class CustomException(Exception):
    '''My Custom Exception'''

def login(username, password):
    '''Logs User In & Creates Session'''
    login_url = "https://www.easistent.com/p/ajax_prijava"
    session = requests.Session()
    data = {
            "uporabnik":username,
            "geslo":password,
            "pin":"",
            "captcha":"",
            "koda":""
            }
    login = session.post(login_url, data=data)
    return login, session

def get_mon(date):
    '''Gets Monday Of Menus'''
    first_day_num = int(date.strftime("%w"))
    # if not 1 (monday) => need to find monday
    if first_day_num == 1:  # 1 == monday
        return date

    # if weekend => goes forwards
    if first_day_num == 6:    # 6 == sat
        monday = date + timedelta(days=2)   # goes to mon
    elif first_day_num == 0:    # 0 == sun
        monday = date + timedelta(days=1)   # goes to mon
    # if workday => backwards
    else:  # if [tue-fri]
        monday = date - timedelta(days=first_day_num - 1)   # goes to mon
    return monday

def send_mail(message):
    print(message)
    
def init_school_info():
    date_today = datetime.now()
    curr_month = int(date_today.strftime("%m"))
    curr_year = int(date_today.strftime("%Y"))

    if path.exists("./school_info.txt"):
        with open("school_info.txt") as f:
            school_info = f.readlines()
            school_info = school_info[0].split("; ")

    else:
        # login
        username = config["username"]
        password = config["password"]
        session = login(username, password)[1]

        # get menu ids
        meals_url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_seznam"
        response = session.get(meals_url)
        soup = BeautifulSoup(response.content, "html.parser")
        # send_mail(str(soup) + '  school')
        id = "ednevnik-seznam_ur_teden"
        meal_ids = []
        for i in range(6):
            meal_id = soup.find(class_=id).find_all("tr")[i + 1]
            if i == 0:
                meal_id = meal_id.find_all("td")[1].get("id")
            else:
                meal_id = meal_id.findChildren()[0].get("id")
            meal_id = meal_id.split("-")[4]
            meal_ids.append(meal_id)

        # get first day of school && set school year
        if curr_month < 9:  # if earlier than september => start of school was year before (curr year - 1)
            school_start_year = curr_year - 1
        else:
            school_start_year = curr_year

        first_day_school = datetime(school_start_year, 9, 1)    # 1st September == first day of school
        first_week_school = get_mon(first_day_school)

        # set school year
        school_year = [curr_year, curr_year + 1]
        school_year_str = json.dumps(school_year)

        meal_ids_str = json.dumps(meal_ids) # reformat meal_ids

        # save to DB
        # if school_info is None:
        with open('school_info.txt', 'w') as f:
            data = f"{school_year_str}; {meal_ids_str}; {first_week_school}"
            f.write(data)
        # else:
        #     with open('school_info.txt', 'w') as f:
        #         data = f"{school_year_str}; {meal_ids_str}; {first_week_school}"
        #         f.write(data)
        return school_year, meal_ids, first_week_school
    return json.loads(school_info[0]), json.loads(school_info[1]), datetime.strptime(school_info[2], FORMAT)

def get_meal_data(week_num, meals, monday):
    # login
    username = config["username"]
    password = config["password"]
    session = login(username, password)[1]
    data = {
            "qversion": 1, #num of tries
            "teden": week_num, #num of week before (if 4 will get 5)
            "smer": "naprej" # direction
            }
    headers = {
            "Content-Type": "application/x-www-form-urlencoded"
            }
    meals_url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_seznam"
    site = session.post(meals_url, data=data, headers=headers)
    soup = BeautifulSoup(site.content, "html.parser")
    id = "ednevnik-seznam_ur_teden"

    #TODO: check disliked foods => prijava/odjava
    #TODO: how to fetch meal selected
    # get meals selected
    week_data = []  # [[meal_text | string, able_to_change | Bool, date | date]]
    for i in range(5):  # for each day of week
        day = monday + timedelta(days=i)
        day = day.strftime("%Y-%m-%d")
        day_data = []
        changed = True
        for meal_id in list(meals.keys()):
            meal_html_id = f"{id}-td-malica-{meal_id}-{day}-0"
            meal_container = soup.find("td", id=meal_html_id)

            # get meal text
            try:
                meal_text = meal_container.find("div").find_all("div")[1].text.strip()
                if meal_text in ["Izbira menija ni več mogoča", "Prijava"]:
                    raise IndexError
            except Exception as e:
                if e == IndexError:
                    # no meal that day => should already be signed off
                    meal_text = ""
                    change = False
                    day_data.append(meal_text)
                    day_data.append(changed)
                    day_data.append(day)
                    day_data.append(meal_id)
                    break
                send_mail(e)
                break
            # get selected meal
            meal_change = meal_container.find("div").find_all("div")[2] # div | could be Naročen(date)Odjava / Odjava
            try:
                meal_option = meal_change.find("a").text.strip()
            except:
                meal_option = ""
            if meal_option and  meal_option == "Prijava":  # could be "Prijava" or "Odjava"
                # not selected meal
                continue
            # if no selected => prijava settings
            # see if can be changed or just be signed off
            if meal_change.find_all("span")[0].text.strip() == "Izbira menija ni več mogoča":    # could be "Naročen" or "Izbira menija ni več mogoča"
                changed = False
                continue
            day_data.append(meal_text)
            day_data.append(changed)
            day_data.append(day)
            day_data.append(meal_id)
            break
        week_data.append(day_data)

    return week_data

def prijava_odjava(session, action, meal_id, date):
    '''
    session = session where logged in
    action = "prijava" or "odjava"
    meal_id = what to change meal to
    date = date of changing menu
    '''
    url = "https://www.easistent.com/dijaki/ajax_prehrana_obroki_prijava"
    data = {
            "tip_prehrane": "malica",
            "id_lokacija": "0",
            "akcija": f"{action}", # either "prijava" or "odjava"
            "id_meni": f"{meal_id}", # meals ids (see main_screen)
            "datum": f"{date}" # date (MainScreen().date_of_menu)
            }
    headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest"
            }
    try:
        response = session.post(url, data=data, headers=headers)
        if not response.json()["status"]: # "ok" if successful "" if unsuccessful
            raise CustomException(f"Unable to change meal for {date}")
        # app.send_notification("Success", "Meal changed", True)
        send_mail(f"Meal_changed for {date}")
        return True
    except Exception as e:
        send_mail(e)
        return False


print("===start===")
def service():
    send_mail("Service started!")
    username = config["username"]
    password = config["password"]
    try:
        _login, session = login(username, password)
        if not _login.json()["status"]:
            raise CustomException("Failed to login!")
        school_year, meal_ids, first_week_school = init_school_info()
        if not meal_ids:
            raise CustomException("no meal_ids")
        meals = {
                meal_ids[0]: "food-drumstick-outline",
                meal_ids[1]: "carrot",
                meal_ids[2]: "food",
                meal_ids[3]: "food-croissant",
                meal_ids[4]: "bowl-mix-outline",
                meal_ids[5]: "basketball"
                }
        today = datetime.now()
        # if weekends => getmonday fetches another week in advance = error
        if today.strftime("%w") == "0":
            today -= timedelta(days=6)
        elif today.strftime("%w") == "6":
            today -= timedelta(days=5)
        monday = get_mon(today + timedelta(days=7))    # gets weeks in advance
        week_num = int(str((monday - first_week_school) / 7).split(" ")[0])
        meals_data = get_meal_data(week_num, meals, monday)
        # check for disliked foods
        disliked_foods = config["disliked_foods"]
        if not disliked_foods:
            send_mail("no disliked foods")
            service()
        selected_menu = config["selected_menu"]    # if Odjava set to selected meal for the day
        selected_menu = list(meals.keys())[int(selected_menu) - 1]
        # compare disliked foods with text
        for meal_data in meals_data:
            for disliked_food in disliked_foods:
                if disliked_food.upper() in meal_data[0]:
                    success = prijava_odjava(session, "prijava", selected_menu, meal_data[2])
                    if not success:
                        prijava_odjava(session, "odjava", meal_data[3], meal_data[2])
                    break
        # sign off or change meal if can be
        # if changing fails still try to sign off
        send_mail("service did well")
        return

    except Exception as e:
        send_mail(e)
        return

if __name__ == "__main__":
    service()
