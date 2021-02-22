print("########### START ###########");
db = db.getSiblingDB("atorin");
db.createCollection("token");
db.token.insert([
    {"_id":"bot","key":"DISCORD_TOKEN"}, //DISCORD BOT TOKEN
    {"_id":"weather","key":"WEATHER_TOKEN"} //OPEN WEATHER MAP API KEY
    {"_id":"statcord","key":"STATCORD_TOKEN"} //STATCORD API KEY
]);
print("########### END ###########");