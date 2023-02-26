## service.py ##

from waiter.waiter import Waiter
import config

config = config.DEFAULT

if __name__ == "__main__":
    waiter = Waiter()   # init Waiter

    # login waiter
    waiter.username = config["username"]
    waiter.password = config["password"]
    waiter.login()

    # provide information
    waiter.default_menu = config["default_menu"]
    waiter.preferred_menu = config["preferred_menu"]
    waiter.favourite_foods = config["favourite_foods"]
    waiter.disliked_foods = config["disliked_foods"]

    # run service
    waiter.service()
