import config from './config.json'

db.tokens.insert([
    {"_id":"bot","key":config.token}, //DISCORD BOT TOKEN
    {"_id":"weather","key":config.weather} //OPEN WEATHER MAP API KEY
])