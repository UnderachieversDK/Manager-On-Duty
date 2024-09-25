import discord
from discord.utils import get
import os
from datetime import datetime
from time import sleep

from pytz import timezone
from DataHandling import DataHandling
from DataHandling import return_meridian
import threading

bot = discord.Bot(case_insensitive=True)

default_color = discord.Color(0x0045BE)
admins = [206636330095083523]
guild_id = 687847569660838009
channel_id = 976619568145514496
role_id = 1288322177099104376

async def checkMOD(broadcast: str = "False", day: str = "False"):
    if day == "False":
        tz = timezone('EST')
        time = datetime.now(tz)
        dateEST = time.strftime("%m-%d")
    else:
        dateEST = day
    needURL = []
    managers = {}
    guild = bot.get_guild(guild_id)
    role = get(guild.roles, id=role_id)
    for member in role.members:
        user = member.id
        if os.path.isfile(f'User Data/{user}/ICS/data.json') == True:
            userData = DataHandling(userID=user, requestInfo=["url", "schedule"])
            if dateEST in userData.scheduleShifts:
                userShifts = userData.scheduleShifts[dateEST]
                managers[user] = [userShifts["Start"], userShifts["End"]]
        else:
            needURL.append(user)
    times = 'Managers:\n'
    for manager in managers:
        manager = await bot.fetch_user(manager)
        name = manager.display_name
        start, end = managers[manager.id]
        times = (f'{times}{name} is on duty today from {return_meridian(start)} to {return_meridian(end)}!\n')
    if broadcast == "True":
        for manager in needURL:
            for admin in admins:
                dm = await bot.fetch_user(admin)
                await dm.send(f'<@{manager}> does not have a working ICS URL! Inform them they can update it at /link or remove their MOD role!')
        broadcast_channel = await bot.fetch_channel(channel_id)
        await broadcast_channel.send(times)
    else:
        return times
    
@bot.command()
async def mods(ctx):
    """ Check manager on duty for the day! """
    result = await checkMOD()
    await ctx.respond(result)

@bot.command()
async def link(ctx, url=str):
    """ Link your MyTLC iCalendar .ics url to link your schedule! """
    if url[0:38] == "https://mytlc.bestbuy.com/public/ical/":
        if url[74:89] == "/myschedule.ics":
            object = DataHandling(userID=ctx.author.id, calURL=url)
            result = object.write_users_ical()
            if result == True:
                object.write_users_url()
                await ctx.respond("Successfully updated your iCalendar schedule link!")
            else:
                await ctx.respond("ICS URL produced no iCalendar file, please copy directly from MyTLC! (Example Link: <https://mytlc.bestbuy.com/public/ical/89ac0c85-j38c-3b5b-bafd-7ce3b61c7b3c/myschedule.ics>)")
        else:
            await ctx.respond("Incorrect ICS URL format, please copy directly from MyTLC! (Example Link: <https://mytlc.bestbuy.com/public/ical/89ac0c85-j38c-3b5b-bafd-7ce3b61c7b3c/myschedule.ics>)")
    else:
        await ctx.respond("Incorrect ICS URL format, please copy directly from MyTLC! (Example Link: <https://mytlc.bestbuy.com/public/ical/89ac0c85-j38c-3b5b-bafd-7ce3b61c7b3c/myschedule.ics>)")

def checkTime():
    sent = False
    threading.Timer(30, checkTime).start()
    tz = timezone('EST')
    time = datetime.now(tz)
    current_time = time.strftime("%H:%M")
    if(current_time == '08:00'):
        if sent != True:
            bot.loop.create_task(checkMOD("True"))
            sent = True
            sleep(90)
            sent = False

checkTime()

bot.run(token)
