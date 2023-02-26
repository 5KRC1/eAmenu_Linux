## config.py ## 

"""
Configuration Of Your eAsistent
'username' => string | account username/email
'password' => string | account password

'disliked_foods' => array | foods you dislike
    foods should be written exactly the same
    as in eAsistent, otherwise it will not work
'selected_menu' => string | type of meal (0-5)
    1 - meni1
    2 - meni2
    3 - meni3
    4 - meni4
    5 - meni5
    6 - meni6
    "Odjava" - odjava

'favourite_foods' => array | foods you enjoy
    foods should be written exactly the same
    as in eAsistent, otherwise it will not work
'default_menu' => string | the meal you are subbed
    to or would like to be subbed to (0-5)
    1 - meni1
    2 - meni2
    3 - meni3
    4 - meni4
    5 - meni5
    6 - meni6
    "Odjava" - odjava
"""

DEFAULT = {
        "username": "",
        "password": "",

        "disliked_foods": [],
        "preferred_menu": "",

        "favourite_foods": [],
        "default_menu": ""
        }
