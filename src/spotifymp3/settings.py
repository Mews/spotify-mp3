from configparser import ConfigParser

def reset_default_configs():
    config = ConfigParser()

    config.add_section("spotify")
    config.set("spotify", "client_id", "<Your client id>")
    config.set("spotify", "client_secret", "<Your client secret>")

    with open("settings.ini", "w", encoding="utf-8") as f:
        config.write(f)

config = ConfigParser()
config.read("settings.ini", encoding="utf-8")

CLIENT_ID = config.get("spotify", "client_id")
CLIENT_SECRET = config.get("spotify", "client_secret")
