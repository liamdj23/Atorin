<p align="center"><img src="https://cdn.discordapp.com/avatars/408959273956147200/d26356dd40d8b76e10c0678b4afe3f1b.webp?size=256"></p>
<h1 align="center">Atorin</h1>
<h3 align="center">Multifunctional bot for your Discord server</h3>
<p align="center"><img alt="Discord" src="https://img.shields.io/discord/408960275933429760?label=discord"> <img alt="Docker Image Size (tag)" src="https://img.shields.io/docker/image-size/liamdj23/atorin/latest"> <img alt="Lines of code" src="https://img.shields.io/tokei/lines/github/liamdj23/Atorin"> <img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/liamdj23/Atorin"></p>
<p align="center"><a href="https://buycoffee.to/liamdj23" target="_blank"><img src="https://buycoffee.to/btn/buycoffeeto-btn-primary.svg" style="width: 150px" alt="Postaw mi kawę na buycoffee.to"></a></p>
<p align="center">🇵🇱 Works only in Polish! 🇵🇱</p>
<p align="center"><a href="https://liamdj23.ovh/addbot">Click here to add Atorin to your Discord Server!</a></p>

# Description

Atorin is Discord Bot written in Python 3.10 using Py-cord.

# Features

- 🎲 Fun
- ⚒️ Moderation
- ℹ️ Information
- 🕹️ Games
- 🎵 Music
- 🌐 Website
- 🐳 Docker

# Installation

1. Install [Python 3.10](https://www.python.org/downloads/), [MongoDB](https://www.mongodb.com/try/download/community) and [Lavalink](https://github.com/freyacodes/Lavalink/releases)([Java](https://aws.amazon.com/corretto/) required)
2. Clone this repo `git clone https://github.com/liamdj23/Atorin.git`
3. Change directory to "Atorin" `cd Atorin`
4. Create virtual environment `python3.10 -m venv venv`
5. Activate virtualenv `source venv/bin/activate`
6. Install dependencies `pip install -r requirements.txt`
7. Fill `config.yml` with token and API keys

# Run

1. Copy service file `sudo cp atorin.service /etc/systemd/system/`
2. Fill service file with valid paths `sudo nano /etc/systemd/system/atorin.service`
3. Enable start at boot `sudo systemctl enable atorin`
4. Run service `sudo systemctl start atorin`
5. Done 🎉

# Docker

Docker images with Atorin are available in [Docker Hub](https://hub.docker.com/r/liamdj23/atorin) for armv7, aarch64 and amd64.

- Pull image `docker pull liamdj23/atorin`
- Run container e.g. `docker run --name atorin -p 8080:8080 -v config.yml:/bot/config.yml liamdj23/atorin`
