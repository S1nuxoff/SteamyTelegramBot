
from steam_web_api import Steam

KEY = "61404ACD9F374B9EB60152E65D50A4C0"
steam = Steam(KEY)

# users = steam.apps.get_user_stats("76561198886382293", '570')
user = steam.users.get_user_details("76561198872044093")
print(user)

