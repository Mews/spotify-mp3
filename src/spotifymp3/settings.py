from configparser import ConfigParser


def reset_default_configs():
    config = ConfigParser()

    config.add_section("spotify")
    config.set("spotify", "client_id", "<Your client id>")
    config.set("spotify", "client_secret", "<Your client secret>")

    with open("settings.ini", "w", encoding="utf-8") as f:
        config.write(f)


def change_config(section, option, new_value):
    config = ConfigParser()
    config.read("settings.ini", encoding="utf-8")

    config.set(section, option, new_value)

    with open("settings.ini", "w", encoding="utf-8") as f:
        config.write(f)


def get_config(section, option):
    config = ConfigParser()
    config.read("settings.ini", encoding="utf-8")

    return config.get(section, option)
