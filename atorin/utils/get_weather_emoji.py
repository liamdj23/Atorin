"""
```yml
    _   _             _       
   / \ | |_ ___  _ __(_)_ __  
  / _ \| __/ _ \| '__| | '_ \ 
 / ___ \ || (_) | |  | | | | |
/_/   \_\__\___/|_|  |_|_| |_|
```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                              
Made with ❤️ by Piotr Gaździcki.

"""


def get_weather_emoji(weather_id: int) -> str:
    thunderstorm = "\U0001F4A8"  # Code: 200's, 900, 901, 902, 905
    drizzle = "\U0001F4A7"  # Code: 300's
    rain = "\U00002614"  # Code: 500's
    snowflake = "\U00002744"  # Code: 600's snowflake
    snowman = "\U000026C4"  # Code: 600's snowman, 903, 906
    atmosphere = "\U0001F301"  # Code: 700's foogy
    clear_sky = "\U00002600"  # Code: 800 clear sky
    few_clouds = "\U000026C5"  # Code: 801 sun behind clouds
    clouds = "\U00002601"  # Code: 802-803-804 clouds general
    hot = "\U0001F525"  # Code: 904
    default = "\U0001F300"  # default emojis

    weather_id_str = str(weather_id)

    if (
        weather_id_str[:1] == "2"
        or weather_id == 900
        or weather_id == 901
        or weather_id == 902
        or weather_id == 905
    ):
        return thunderstorm
    elif weather_id_str[:1] == "3":
        return drizzle
    elif weather_id_str[:1] == "5":
        return rain
    elif weather_id_str[:1] == "6" or weather_id == 903 or weather_id == 906:
        return snowflake + " " + snowman
    elif weather_id_str[:1] == "7":
        return atmosphere
    elif weather_id == 800:
        return clear_sky
    elif weather_id == 801:
        return few_clouds
    elif weather_id == 802 or weather_id == 803 or weather_id == 804:
        return clouds
    elif weather_id == 904:
        return hot
    else:
        return default
