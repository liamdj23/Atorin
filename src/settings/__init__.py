import json

main_file = {
    "token": "DISCORD_TOKEN"
}


class Settings:
    def __init__(self):
        try:
            with open("settings/main.json") as f:
                self.main = json.load(f)
        except FileNotFoundError:
            with open("settings/main.json", 'w', encoding="utf-8") as f:
                json.dump(main_file, f, ensure_ascii=False, indent=4)
                print("Config file created. Go to settings directory and fill the file.")
                raise SystemExit


if __name__ == '__main__':
    Settings()
