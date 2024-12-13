import os
import squad_depth_gen as sdg
import discord
import time
from matplotlib import pyplot as plt
import pickle
import json
import matches as mt
import FT_Quiz as ftq
import table as tbl
import random
import asyncio
from time import sleep
from discord.utils import get
from keep_running import running
from discord.ext import commands, tasks

from dotenv import load_dotenv, dotenv_values
from datetime import datetime, timedelta

td = datetime.today()

load_dotenv()
running()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
with open('club_logo.dat', 'rb') as f:
    logo = pickle.load(f)

intents = discord.Intents.all()
client = discord.Client(intents=intents)

def matches(list):
    scores = []
    date = str(list[0][0][0]) + "-" + list[0][0][1]
    for match in list:
        #date="  ".join([match[0]])
        score = " ".join(match[1])
        scores.append(score)
    scores = "\n".join(scores)
    return scores, date

def news():
    from aiff_news import get_news
    news, img = get_news()
    title = "\n".join(["\n".join([b, a]) for a, b in news.items()])
    embed = discord.Embed(title="**Latest News**",
                          description=title,
                          color=0x4cfa11)
    embed.set_image(url=img)
    return embed

def otd(today):
    with open("OTD.json","r") as f:
        dct=json.load(f)
        try:
            events=dct[today]
            st="\n\n".join(events)
        except:
            st=""
    if st=="":
        return
    embed=discord.Embed(title="On This Day",description=st,color=0x4cfa11)
    return embed

def sim():
    goals = [0, 0]
    for i in range(5):
        team1 = random.random()
        team2 = random.random()
        if team1 >= 0.5:
            goals[0] += 1
        if team2 >= 0.5:
            goals[1] += 1
        if abs(goals[0] - goals[1]) > (4 - i):
            break
    if goals[0] == goals[1]:
        while True:
            team1 = random.random()
            team2 = random.random()
            if team1 >= 0.5:
                goals[0] += 1
            if team2 >= 0.5:
                goals[1] += 1
            if goals[0] != goals[1]:
                break
    return goals

def eval_result(predict_dct):
    try:
        with open("prediction_results.dat", "rb") as f:
            points = pickle.load(f)
    except:
        points = {}
    results = predict_dct["Results"]
    predictions = predict_dct["Predictions"]
    for i, j in predictions.items():
        points.setdefault(i, 0)
        for k in range(len(j)):
            match = j[k]
            pr = results[k]
            if match[1][0] == pr[1][0] and match[1][1] == pr[1][1]:
                points[i] += 5
            elif match[1][0] - match[1][1] == 0 and pr[1][0] - pr[1][
                    1] == 0:  #Draw
                points[i] += 3
            elif match[1][0] - match[1][1] > 0 and pr[1][0] - pr[1][
                    1] > 0:  #Home Win
                points[i] += 3
            elif match[1][0] - match[1][1] < 0 and pr[1][0] - pr[1][
                    1] < 0:  #Away Win
                points[i] += 3
    return points

def match_embed():
    from aiff_matches import match_today, match_yest
    today = match_today()
    desc = ""
    if len(today) != 0:
        match, date = matches(today)
    else:
        match = "No matches today"
    td = datetime.today()
    date = td.strftime("%d-%b, %Y")
    yest = match_yest()
    if len(yest) != 0:
        match1, date1 = matches(yest)
    else:
        match1 = "No matches yesterday"
    date1 = (td - timedelta(1)).strftime("%d-%b, %Y")
    desc="**Yesterday:\t\t"+date1+"**\n\n"+match1+\
    "\n\n**Today:\t\t"+date+"**\n\n"+match
    embed = discord.Embed(title="Match Report  (View Details)",
                          description=desc,
                          url="https://the-aiff.com",
                          color=0x2027f7)
    return embed


@tasks.loop(seconds=60)
async def match_report():
    for guild in client.guilds:
        if guild.name == GUILD:
            now = datetime.now()
            if now.strftime("%H:%M") == "03:00":  #8:30AM IST in GMT
                channel_id = 735387831928619023  #Football_India channel
                role = get(guild.roles, name="matchday")
                channel = client.get_channel(channel_id)
                now = datetime.now()
                embed = news()
                otd_embed=otd(now.strftime("%d %b").upper())
                await channel.send(embed=embed)
                embed = match_embed()
                await channel.send(role.mention, embed=embed)
                try:
                    await channel.send(embed=otd_embed)
                except:
                    pass


@client.event
async def on_ready():
    match_report.start()
    for guild in client.guilds:
        if guild.name == GUILD:
            print(guild.name)
            print(guild.id)

        print('{} is connected to the following guild:\n'.format(client.user))
        print('{}, (id: {})'.format(guild.name, guild.id))

try:
    flag = 0

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.content.startswith("!if"):

            if "say" in message.content:
                if message.author.id==735365973896593510:
                    text=message.content.split("say")[-1]
                    if "," in text:
                        text=text.partition(",")
                        cnl=text[0].strip(" <>#")
                        msg=text[-1]
                        channel=client.get_channel(int(cnl))
                    else:
                        channel=message.channel
                        msg=text
                    await channel.send(str(msg))
                return
            if "reply" in message.content:
                if message.author.id==735365973896593510:
                        text=message.content.split("reply")[-1]
                        if "," in text:
                            text=text.partition(",")
                            st=text[0].split('/')
                            cnl,rep=int(st[-2]),int(st[-1])
                            channel=client.get_channel(cnl)
                            msg=text[-1]
                            reply_msg=await channel.fetch_message(rep)
                            await reply_msg.reply(msg)
                return
            if "help" in message.content:  #Help command
                string = "Prefix-   ```!if```\n\n\n**help**:\t\tShows this Menu\n\n**matches:**\t\tShows Match Report from the day before and fixtures for the current date\n\n**squad (League,Year,Club)**:\t\tShows the squad for given season by position along with the number of appearance in that position\n(Example: !if matches ISL,2021,Kerala)\n\n**news**:\t\tReturns the latest news and updates from Indian Football\n\n**quiz (Number of questions)**:\t\tPlay different types quiz on Indian Football- No.of questions is 20 by default\n\n**passmap <match_number>**:\t\t to get the pass network of both teams from a given match in ISL 2021-22 season\n\n**penalty**:\t\tPlay penalty shootout game on Discord in either 2 modes: 1- Friendly mode 2- Tournament mode"
                embed = discord.Embed(title="**Help Menu**",
                                      description=string,
                                      color=0x4cfa11)
                await message.channel.send(embed=embed)
            if "news" in message.content:
                embed = news()
                await message.channel.send(embed=embed)
            if "matches" in message.content:
                embed = match_embed()
                await message.channel.send(embed=embed)
            if "passmap" in message.content:
                try:
                    num = message.content.split("passmap")[-1].strip()
                    match, st = mt.avg_position(int(num) - 1)
                    embed = discord.Embed(title=match, description=st)
                    with open("Figure_1-1.png", "rb") as f:
                        img = discord.File(f)
                        embed.set_image(url="attachment://Figure_1-1.png")
                    embed.set_footer(text="Credits- StatsBomb.com")
                    await message.channel.send(embed=embed, file=img)
                except:
                    await message.channel.send(
                        "Use format !if passmap <match_number>\nExample- !if lineup 115"
                    )
            if "penalty" in message.content:

                async def shoot():
                    def check(msg):
                        return msg.author == message.author and msg.channel == message.channel

                    await message.channel.send(
                        "Enter direction to score: (L/C/R): ")
                    wrong = 0
                    while wrong <= 3:
                        msg = await client.wait_for('message',
                                                    check=check,
                                                    timeout=60)
                        pos = msg.content.upper()
                        if pos == "CANCEL":
                            await message.channel.send("Match cancelled")
                            flag = 0
                            return
                        elif pos not in ("L", "R", "C"):
                            await message.channel.send(
                                "Wrong direction entered, Try Again")
                        else:
                            break
                        wrong += 1
                    else:
                        await message.channel.send(
                            "Too many mistakes, Match cancelled")
                        flag = 0
                        return
                    ch = random.choice(("L", "R", "C"))
                    await message.channel.send(
                        "You shoot towards the {} and the {} keeper jumps towards the {}"
                        .format(posdct[pos], match[1], posdct[ch]))
                    time.sleep(1)
                    if pos == ch:
                        await message.channel.send("MISSED! " + match[1] +
                                                   " saved the shot! :open_hands:")
                        x = 0
                    else:
                        await message.channel.send("GOOAALL! " + match[0] +
                                                   " scores :soccer:")
                        x = 1
                    await message.channel.send(
                        "Enter direction to save: L/C/R: ")
                    wrong = 0
                    while wrong < 3:
                        msg = await client.wait_for('message',
                                                    check=check,
                                                    timeout=60)
                        pos = msg.content.upper()
                        if pos == "CANCEL":
                            await message.channel.send("Match cancelled")
                            flag = 0
                            return
                        elif pos not in ("L", "R", "C"):
                            await message.channel.send(
                                "Wrong direction entered, Try Again")
                        else:
                            break
                        wrong += 1
                    else:
                        await message.channel.send(
                            "Too many mistakes, Match cancelled")
                        flag = 0
                        return
                    ch = random.choice(("L", "R", "C"))
                    await message.channel.send(
                        "You jump towards the {} and {} takes the penalty towards the {}"
                        .format(posdct[pos], match[1], posdct[ch]))
                    time.sleep(1)
                    if pos == ch:
                        await message.channel.send("You Saved! :open_hands: ")
                        y = 0
                    else:
                        await message.channel.send(match[1] + " scored :soccer:")
                        y = 1
                    return (x, y)

                global flag
                if flag == 1:
                    await message.channel.send(
                        "Wait, Match in Progress, Try again later")
                    return
                import penalty
                team_abbv = {"Bengaluru FC": "BFC",
                    "Chennaiyin FC": "CFC",
                    "East Bengal FC": "EBFC",
                    "FC Goa": "FCG",
                    "Hyderabad FC": "HFC",
                    "Jamshedpur FC": "JFC",
                    "Kerala Blasters": "KBFC",
                    "Mohun Bagan SG": "MBSG",
                    "Mumbai City FC": "MCFC",
                    "Northeast United": "NEUFC",
                    "Odisha FC": "OFC",
                    "Punjab FC": "PFC",
                    "Delhi FC":"DFC",
                    "Gokulam Kerala":"GKFC",
                    "Inter Kashi":"INT",
                    "Mohammedan SC":"MSC",
                    "Real Kashmir FC":"RKFC",
                    "NEROCA FC":"NFC",
                    "TRAU FC":"TFC",
                    "Namdhari FC":"NFC"
}
                team_logo = {"Bengaluru FC": "<:Bengaluru_FC:735721059222814730>",
                    "Chennaiyin FC": "<:Chennaiyin_FC:735721016935841854>",
                    "Delhi FC":"<:DelhiFC:896435379790573648>",
                    "East Bengal FC": "<:East_Bengal_FC:1126388137980076072>",
                    "Gokulam Kerala":"<:Gokulam_Kerala:735735188708917310>",
                    "FC Goa": "<:FC_Goa:735720980881604608>",
                    "Hyderabad FC": "<:Hyderabad_FC:743665597228777493>",
                    "Inter Kashi":"<:Inter_Kashi:1126386557767667792>",
                    "Jamshedpur FC": "<:Jamshedpur_FC:735720921926598676>",
                    "Kerala Blasters": "<:Kerala_Blasters:735720770767945818>",
                    "Mohammedan SC":"<:MohammedanSC:736457854357209179>",
                    "Mohun Bagan SG": "<:Mohun_Bagan_SG:1126398923569909841>",
                    "Mumbai City FC": "<:Mumbai_City_FC:735720893124313150>",
                    "Northeast United": "<:Northeast_United:735720865920188546>",
                    "Odisha FC": "<:Odisha_FC:735720833653145670>",
                    "Punjab FC": "<:Punjab_FC:1129385537334153276>",
                    "Real Kashmir FC":"<:Real_Kashmir:735735098326122586>",
                    "NEROCA FC":"<:NEROCA:735734830867808299>",
                    "TRAU FC":"<:TRAU:735755565887914096>",
                    "Namdhari FC":"<:Namdhari_FC:1126386937788375080>"
                        
                }
                posdct = {"L": "left", "R": "right", "C": "centre"}
                stage = {0: "Quarter Final", 1: "Semi Final", 2: "Final"}
                stage_pts = {0: 25, 1: 50, 2: 100}

                def check(msg):
                    return msg.author == message.author and msg.channel == message.channel
                desc = ""
                user_id = message.author.id
                string = "React with appropiate emoji to start game\n\n:one: Friendly match    :two: Tournament mode"
                embed = discord.Embed(title="Game Menu", description=string)
                embed.set_image(url="https://img.freepik.com/free-vector/soccer-penalty-kick-scene-poster_603843-319.jpg?w=740&t=st=1695274281~exp=1695274881~hmac=0ff73b3c26972ff7b741a4a3111ed261d1bd0777530f36b5ac7c599ae1e14e2f")
                msg = await message.channel.send(embed=embed)
                emojis = ["1️⃣", "2️⃣"]
                for emoji in emojis:
                    await msg.add_reaction(emoji)

                def check1(r, u):
                    return u.id == message.author.id and r.message.channel.id == message.channel.id and str(
                        r.emoji) in emojis

                try:
                    reaction, user = await client.wait_for('reaction_add',
                                                           check=check1,
                                                           timeout=30)
                    if str(reaction.emoji) == "1️⃣":
                        mode = 0
                    elif str(reaction.emoji) == "2️⃣":
                        mode = 1
                    else:
                        await message.channel.send("Wrong choice")
                        return
                except asyncio.TimeoutError:
                    await message.channel.send("Game Cancelled")
                    return
                with open("game.dat", "rb") as f:
                    table = pickle.load(f)
                table.setdefault(user_id, 0)
                teams = list(team_abbv.keys())
                #teams.sort()
                for i in range(len(teams)):
                    desc = desc + str(i + 1) + ": " + teams[i] + "\n"
                embed = discord.Embed(
                    title="**Choose a team below⬇️** (Format: your_team_no,opponent_no)",
                    description="```" + desc+"```",
                    color=0x4cfa11)
                embed.set_footer(text="Example: 3,8\nType CANCEL to cancel")
                selection_msg= await message.channel.send(embed=embed)
                try:
                    msg = await client.wait_for('message',
                                                check=check,
                                                timeout=30)
                    if "cancel" in msg.content.strip():
                        await message.channel.send("Cancelled")
                        return
                    try:
                        if "," in msg.content.strip():
                            t= msg.content.strip().partition(",")
                            t1,t2=int(t[0].strip())-1,int(t[-1].strip())-1
                            team,team2 = teams[t1],teams[t2]
                        else:
                            team = teams[int(msg.content.strip()) - 1]
                            teams.remove(team)
                            team2=random.choice(teams)
                    except:
                        await message.channel.send("Wrong choice, Try again")
                        flag = 0
                        return
                    flag = 1
                    random.shuffle(teams)
                    if mode == 1:
                        teams = teams[:7]
                        teams.append(team)
                        matches = list(
                            zip(teams[:len(teams) // 2],
                                teams[len(teams) // 2:]))
                        match_dct = {}
                        score_dct = {}
                        match_dct[0] = matches
                        random.shuffle(matches)
                        penalty.fixtures(list(match_dct.values()))
                        embed = discord.Embed()
                        with open("bracket_img.png", "rb") as f:
                            img = discord.File(f)
                            embed.set_image(url="attachment://bracket_img.png")
                        await message.channel.send(embed=embed, file=img)
                        await asyncio.sleep(4)

                    for k in range(3):
                        rev = False
                        results = []
                        fixtures = []
                        if mode == 1:
                            for j in range(len(matches)):
                                m = matches[j]
                                if team in m:
                                    match = m
                                    p = j
                                else:
                                    g1, g2 = sim()
                                    if g1 > g2:
                                        fixtures.append(m[0])
                                    else:
                                        fixtures.append(m[1])
                                    results.append((g1, g2))
                            await message.channel.send("**" + stage[k] + "**")
                        else:
                            match = [team,team2]
                        score = []

                        async def show_result(table):
                            embed = discord.Embed()
                            embed = discord.Embed(
                                title="**Result**",
                                description=
                                "{} {} {}-{} {} {}\n\n**Your Total Points:**  {}".
                                format(match[0],team_logo[match[0]], sc[0], sc[1],team_logo[match[1]],match[1],
                                       table[user_id]),
                                color=0x4cfa11)
                            await message.channel.send(embed=embed)
                            with open("game.dat", "wb") as f:
                                pickle.dump(table, f)

                        if match[0] != team:
                            rev = True
                            match = list(match)
                            match.reverse()
                        team1, team2 = team_abbv[match[0]], team_abbv[match[1]]
                        await message.channel.send("Your team is: " + match[0] +
                                                   "\n" +
                                                   "Your opponent is: " +
                                                   match[1])
                        string="{} :vs: {}".format(team_logo[match[0]],team_logo[match[1]])
                        await message.channel.send(string)
                        embed = discord.Embed()
                        for i in range(5):
                            x = await shoot()
                            if x == None:
                                return
                            score.append(x)
                            sc = penalty.shootout((team1, team2), score)
                            with open("game_img.png", "rb") as f:
                                img = discord.File(f)
                                embed.set_image(
                                    url="attachment://game_img.png")
                            await message.channel.send(embed=embed, file=img)

                            if abs(sc[0] - sc[1]) > (4 - i):
                                break
                        if sc[0] > sc[1]:
                            await message.channel.send(
                                "Congratulations, You won! +10 pts")
                            if mode == 1:
                                fixtures.insert(p, match[0])
                                matches = list(
                                    zip(fixtures[::2], fixtures[1::2]))
                                result = [sc[0], sc[1]]
                                if rev:
                                    result.reverse()
                                results.insert(p, result)
                                score_dct[k] = results
                                match_dct[k + 1] = matches
                                penalty.fixtures(list(match_dct.values()),
                                                 list(score_dct.values()))
                                with open("bracket_img.png", "rb") as f:
                                    img = discord.File(f)
                                    embed.set_image(
                                        url="attachment://bracket_img.png")
                                await message.channel.send(embed=embed,
                                                           file=img)
                                await message.channel.send(
                                    ".\n\nYou have won " + str(stage_pts[k]) +
                                    " for winning the " + str(stage[k]))
                                await asyncio.sleep(5)
                                table[user_id] += stage_pts[k]
                                await show_result(table)
                            else:
                                table[user_id] += 10
                                await show_result(table)
                                break

                        elif sc[0] < sc[1]:
                            await message.channel.send("Sorry, You lost")
                            await show_result(table)
                            break
                        else:
                            await message.channel.send(
                                "Match heads towards sudden death")
                            while True:
                                x = await shoot()
                                if x == None:
                                    return
                                score.append(x)
                                sc = penalty.shootout((team1, team2), score)
                                with open("game_img.png", "rb") as f:
                                    img = discord.File(f)
                                    embed.set_image(
                                        url="attachment://game_img.png")
                                await message.channel.send(embed=embed,
                                                           file=img)
                                if sc[0] != sc[1]:
                                    break
                            if sc[0] > sc[1]:
                                await message.channel.send(
                                    "Congratulations, You won! +5 Pts")
                                if mode == 1:
                                    fixtures.insert(p, match[0])
                                    matches = list(
                                        zip(fixtures[::2], fixtures[1::2]))
                                    result = [sc[0], sc[1]]
                                    if rev:
                                        result.reverse()
                                    results.insert(p, result)
                                    score_dct[k] = results
                                    match_dct[k + 1] = matches
                                    penalty.fixtures(list(match_dct.values()),
                                                     list(score_dct.values()))
                                    with open("bracket_img.png", "rb") as f:
                                        img = discord.File(f)
                                        embed.set_image(
                                            url="attachment://bracket_img.png")
                                    await message.channel.send(embed=embed,
                                                               file=img)
                                    await message.channel.send(
                                        ".\n\nYou have won " +
                                        str(stage_pts[k]) +
                                        " for winning the " + str(stage[k]))
                                    await asyncio.sleep(5)
                                    table[user_id] += stage_pts[k]
                                    await show_result(table)
                                else:
                                    table[user_id] += 5
                                    await show_result(table)
                                    break
                            elif sc[0] < sc[1]:
                                await message.channel.send("Sorry, You lost")
                                await show_result(table)
                                break

                except asyncio.TimeoutError:
                    await message.channel.send("Match Cancelled")
                flag = 0
            if "'league" in message.content:
                roles = message.author.roles
                for role in roles:
                    if u"President" in role.name or u"Referee" in role.name:
                        emojis = ["1️⃣", "2️⃣", "3️⃣"]
                        string = "1️⃣\tCreate New League (Moderators only)\n\n2️⃣\tShow Table\n\n3️⃣\tEnter Results (Moderators only)\n\n"
                    else:
                        emojis = ["2️⃣"]
                        string = "2️⃣\tShow Table\n\n"
                embed = discord.Embed(title="League Menu", description=string)
                message1 = await message.channel.send(embed=embed)
                for emoji in emojis:
                    await message1.add_reaction(emoji)
    
                def check1(msg):
                    return msg.author == message.author and msg.channel == message.channel
    
                def check(r, u):
                    return u.id != client.user.id and r.message.channel.id == message.channel.id and str(
                        r.emoji) in emojis and str(r.emoji) in emojis
    
                try:
                    reaction, user = await client.wait_for('reaction_add',
                                                           check=check,
                                                           timeout=30)
                except asyncio.TimeoutError:
                    await message.channel.send("Time Out")
                    return
                if reaction.emoji == "1️⃣":
                    for role in user.roles:
                        if u"President" in role.name or u"Referee" in role.name:
                            flag = 1
                    if flag == 0:
                        await message.channel.send(
                            "You don't have appropiate roles.")
                    elif flag == 1:
                        await message.channel.send(
                            "Are you sure you want to create a new table? Previous table will be deleted"
                        )
                        try:
                            msg = await client.wait_for('message',
                                                        check=check1,
                                                        timeout=30)
                            if msg.content.lower() != "yes":
                                end, dump = True, False
                                await message.channel.send("Cancelled")
                            else:
                                table_dct = {}
                        except asyncio.TimeoutError:
                            await message.channel.send("Cancelled")
                            return
                        try:
                            await message.channel.send(
                                    "Enter teams (Separated by comma ','): "
                                )
                            msg1 = await client.wait_for('message',
                                                             check=check1,
                                                             timeout=150)
                            await message.channel.send(
                                    "Enter number of groups: "
                                )
                            msg2 = await client.wait_for('message',
                                                             check=check1,
                                                             timeout=30)
                        except asyncio.TimeoutError:
                            run=0
                            await message.channel.send("Cancelled")
                            return
                        team_lst=msg1.content.split(',')
                        grps=int(msg2.content)
                        grp_dct=tbl.group_draw(team_lst,grps)
                        st=""
                        confirm=0
                        groups=list(grp_dct.keys())
                        groups.sort()
                        for i in groups:
                            st=st+"\n\n**Group "+i+"**\n"+"\n".join(grp_dct[i])
                        grp_embed=discord.Embed(title="Groups",description=st,color=0xfa3e48)
                        grp_embed.set_footer(text="🔴Randomize, ✅Confirm")
                        embed_msg= await message.channel.send(embed=grp_embed)
                        emojis=["🔴","✅"]
                        for emoji in emojis:
                            await embed_msg.add_reaction(emoji)
                        try:
                            while confirm!=True:
                                reaction, user = await client.wait_for('reaction_add',
                                                                           check=check,
                                                                           timeout=60)
                                if reaction.emoji=="🔴":
                                    await embed_msg.remove_reaction("🔴",user)
                                    st=""
                                    grp_dct=tbl.group_draw(team_lst,grps)
                                    groups=list(grp_dct.keys())
                                    groups.sort()
                                    for i in groups:
                                        teams=grp_dct[i]
                                        random.shuffle(teams)
                                        st=st+"\n\n**Group "+i+"**\n"+"\n".join(teams)
                                    grp_embed=discord.Embed(title="Groups",description=st,color=0xfa3e48)
                                    grp_embed.set_footer(text="🔴Randomize, ✅Confirm")
                                    await embed_msg.edit(embed=grp_embed)                                    
                                elif reaction.emoji=="✅":
                                    grp_embed=discord.Embed(title="Groups",description=st,color=0x4af53b)
                                    grp_embed.set_footer(text="✅Confirmed")
                                    await embed_msg.edit(embed=grp_embed)
                                    confirm=True
                                    
                        except asyncio.TimeoutError:
                            await message.channel.send("Time Out")
                        
                            
            if "leaderboard" in message.content or "lb" in message.content:
                with open("game.dat", "rb") as f:
                    table = pickle.load(f)
                lst = sorted(table.items(), key=lambda kv: kv[1], reverse=True)
                user_id = message.author.id
                pts = table[user_id]
                st = "Your Points: " + str(pts) + "\n\n"
                for i in range(len(lst[:15])):
                    try:
                        user = await client.fetch_user(lst[i][0])
                        user = str(user.name)
                    except discord.errors.NotFound:
                        user = "@Deleted_User"
                    st = st + str(i + 1) + "-  **" + str(user) + "**:   " + str(
                        lst[i][1]) + "\n"

                embed = discord.Embed(title="**Leaderboard (Top 15)**   Unique players="+str(len(lst)),
                                      description=st,
                                      color=0x4cfa11)
                await message.channel.send(embed=embed)
            if "squad" in message.content:  #Squad Command
                msg = message.content.partition("squad")[-1]
                seasons = [
                    "2014", "2015", "2016", "2017", "2018", "2019", "2020",
                    "2021","2022"
                ]
                leagues = ["isl", "i-league"]
                if True:
                    data = msg.split(',')
                    league = data[0].strip().lower()
                    season = data[1].strip()
                    if league not in leagues:
                        await message.channel.send("League not in database.")
                        raise ValueError
                    if season not in seasons:
                        await message.channel.send("Season out of range.")
                        raise ValueError
                    club = data[-1].strip()
                player_dict, team = list(
                    sdg.get_squadepth(
                        20, league, season, team=club).values()), list(
                            sdg.get_squadepth(3, league, season,
                                              team=club).keys())[0]
                string = ""
                pkeys = [
                    u'Goalkeeper', u'Left-Back', u'Sweeper', u'Centre-Back',
                    u'Right-Back', u'Defensive Midfield', u'Central Midfield',
                    u'Left Midfield', u'Left Winger', u'Right Midfield',
                    u'Right Winger', u'Attacking Midfield', u'Second Striker',
                    u'Centre-Forward'
                ]
                for p in pkeys:
                    if len(player_dict[0][p]) > 0:
                        string = string + "**" + p + "**" + ":  " + "; ".join(
                            player_dict[0][p]) + "\n"
                        embed = discord.Embed(title="\t\t**" + team + '**\n\n',
                                              description=string,
                                              color=0x4cfa11)
                embed.set_thumbnail(url=logo[team])
                await message.channel.send(embed=embed)
            if "quiz" in message.content:
                try:
                    stop = False
                    pts_table = {}
                    string = "React with appropiate emoji to start quiz\n\n:one: Choose the correct option\n:two: Guess the player\n:three: Guess the flag"
                    embed = discord.Embed(title="Quiz Menu",
                                          description=string)
                    msg = await message.channel.send(embed=embed)
                    emojis = ["1️⃣", "2️⃣","3️⃣"]
                    for emoji in emojis:
                        await msg.add_reaction(emoji)

                    def check(r, u):
                        return u.id == message.author.id and r.message.channel.id == message.channel.id and str(
                            r.emoji) in emojis

                    try:
                        reaction, user = await client.wait_for('reaction_add',
                                                               check=check,
                                                               timeout=15)
                        if str(reaction.emoji) == "1️⃣":
                            q_type = 0
                        elif str(reaction.emoji) == "2️⃣":
                            q_type = 1
                        elif str(reaction.emoji) == "3️⃣":
                            q_type = 2
                    except asyncio.TimeoutError:
                        await message.channel.send("Quiz Cancelled")
                        return
                    args = message.content.strip("!if quiz")
                    q_no = args[0:]
                    if int(q_no) > 30:
                        q_no = 20
                    if q_no == '':
                        q_no = 10
                except:
                    q_no = 10

                def check(msg):
                    return msg.author != client.user and msg.channel == message.channel

                if q_type == 0:
                    ob = ftq.Quiz(int(q_no), 0)
                    questions, answers, options = ob.quiz()
                    s = "Choose the correct option:"
                    await message.channel.send(s)
                    await asyncio.sleep(2)

                    for i in range(len(questions)):
                        await asyncio.sleep(3)
                        q = questions[i]
                        ans = answers[i]
                        option = options[i]
                        wrong = 0
                        await message.channel.send(q)
                        while wrong < 10:
                            try:
                                msg = await client.wait_for('message',
                                                            check=check,
                                                            timeout=20)
                                try:
                                    if msg.content.lower() in ["stop",'cancel']:
                                        await message.channel.send("Stopped")
                                        stop = True
                                        break
                                    elif option[msg.content.upper()] == ans:
                                        await message.channel.send(
                                            "Correct  " + msg.author.mention)
                                        if msg.author not in pts_table.keys():
                                            pts_table[msg.author] = 1
                                        else:
                                            pts_table[msg.author] += 1
                                        break
                                    else:
                                        wrong += 1
                                except KeyError:
                                    wrong += 1
                            except asyncio.TimeoutError:
                                await message.channel.send("\nTime's up! ")
                                break
                        else:
                            await message.channel.send(
                                "Wrong Answer, Correct answer is- " + str(ans))
                        if stop == True:
                            break

                if q_type >= 1:
                    obj = ftq.Quiz(int(q_no), q_type)
                    questions, answers, options = obj.quiz()
                    num = 1
                    for i in range(len(questions)):
                        if stop == True:
                            break
                        await asyncio.sleep(3)
                        q, ans = questions[i], answers[i]
                        embed = discord.Embed(title="Question " + str(num) +
                                              ".")
                        num += 1
                        embed.set_image(url=q)
                        await message.channel.send(embed=embed)
                        wrong = 0
                        while wrong < 10:
                            try:
                                msg = await client.wait_for('message',
                                                            check=check,
                                                            timeout=20)
                                if msg.content.lower() == ans.lower():
                                    await message.channel.send(
                                        "Correct  " + msg.author.mention)
                                    if msg.author not in pts_table.keys():
                                        pts_table[msg.author] = 1
                                    else:
                                        pts_table[msg.author] += 1
                                    break
                                elif msg.content.lower() in ["stop","cancel"]:
                                    await message.channel.send("Stopped")
                                    stop = True
                                else:
                                    wrong += 1
                            except asyncio.TimeoutError:
                                await message.channel.send(
                                    "\nTime's up! Correct answer is- " +
                                    str(ans))
                                break
                        else:
                            await message.channel.send(
                                "Wrong Answer, Correct answer is- " + str(ans))
                lst = sorted(pts_table.items(),
                             reverse=True,
                             key=lambda kv: kv[1])
                lst1 = list(zip(*lst))
                plt.figure(facecolor="black")
                ax = plt.axes()
                ax.set_facecolor("black")
                ax.tick_params(colors="yellow", which='both')
                ax.spines['left'].set_color('yellow')
                try:
                    plt.bar(range(len(pts_table)), lst1[1], color="blue")
                    plt.xticks(range(len(pts_table)), lst1[0], color="yellow")
                except:
                    plt.bar(0, 0, color="blue")
                if len(lst1[0]) == 1:
                    plt.xlim([0, len(lst1[0])])
                plt.savefig("image.png", format="png")
                plt.close()
                embed = discord.Embed(title="Points Table")
                with open("image.png", "rb") as f:
                    img = discord.File(f)
                    embed.set_image(url="attachment://image.png")
                await message.channel.send(embed=embed, file=img)
                s = ""
                for i, j in lst:
                    s = s + str(i) + "\t\t" + str(j) + "\n"
                await message.channel.send(
                    "```Quiz completed, Results:\n\n{}```".format(s))
        if message.content.startswith("!if predict"):
            flag = 0
            lst = []
            dump = True
            end = False
            roles = message.author.roles
            for role in roles:
                if u"President" in role.name or u"Referee" in role.name:
                    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
                    string = "1️⃣\tAdd new matches (Moderators only)\n\n2️⃣\tPredict in available matches\n\n3️⃣\tShow your predictions\n\n4️⃣\tEnter results (Moderators only)\n\n"
                else:
                    emojis = ["2️⃣", "3️⃣"]
                    string = "2️⃣\tPredict in available matches\n\n3️⃣\tShow your predictions\n\n"
            embed = discord.Embed(title="Prediction Menu", description=string)
            message1 = await message.channel.send(embed=embed)
            for emoji in emojis:
                await message1.add_reaction(emoji)

            def check1(msg):
                return msg.author == message.author and msg.channel == message.channel

            def check(r, u):
                return u.id != client.user.id and r.message.channel.id == message.channel.id and str(
                    r.emoji) in emojis and str(r.emoji) in emojis

            try:
                reaction, user = await client.wait_for('reaction_add',
                                                       check=check,
                                                       timeout=30)
            except asyncio.TimeoutError:
                await message.channel.send("Time Out")
                return
            if reaction.emoji == "1️⃣":
                for role in user.roles:
                    if u"President" in role.name or u"Referee" in role.name:
                        flag = 1
                if flag == 0:
                    await message.channel.send(
                        "You don't have appropiate roles.")
                elif flag == 1:
                    await message.channel.send(
                        "Are you sure you want to enter a new set of matches? Previous entry will be deleted"
                    )
                    try:
                        msg = await client.wait_for('message',
                                                    check=check1,
                                                    timeout=30)
                        if msg.content.lower() != "yes":
                            end, dump = True, False
                            await message.channel.send("Cancelled")
                        else:
                            predict_dct = {}
                    except asyncio.TimeoutError:
                        end, dump = True, False
                        await message.channel.send("Cancelled")
                        return
                    while end == False:
                        try:
                            await message.channel.send(
                                "Enter match for prediction (Format- Team 1 vs  Team 2)"
                            )
                            msg1 = await client.wait_for('message',
                                                         check=check1,
                                                         timeout=30)
                            try:
                                team1, x, team2 = msg1.content.partition(
                                    " vs ")
                            except:
                                await message.channel.send(
                                    "Wrong format, Cancelled")
                            lst.append([team1.upper(), team2.upper()])
                            await message.channel.send("Add more matches? ")
                            msg = await client.wait_for('message',
                                                        check=check1,
                                                        timeout=30)
                            if msg.content.lower() != "yes":
                                end = True
                                await message.channel.send("Done!")
                        except asyncio.TimeoutError:
                            end, dump = True, False
                            await message.channel.send("Cancelled")
                            return
                    predict_dct["Matches"] = lst
                    predict_dct["Predictions"] = {}
                    predict_dct["Results"] = []
                    try:
                        with open("predict_matches.dat", "rb") as f:
                            dct1 = pickle.load(f)

                        dct = dct1["Predictions"]
                        lst = dct1["Results"]
                        for i in range(len(lst)):
                            match = lst[i]
                            lst[i] = ("{} {}-{} {}".format(
                                match[0][0], str(match[1][0]),
                                str(match[1][1]), match[0][1]))
                        string1 = "\n\nResults:\n" + "\n".join(lst)
                        string = ""
                        for i, j in dct.items():
                            lst2 = []
                            for match in j:
                                lst2.append("{} {}-{} {}".format(
                                    match[0][0], str(match[1][0]),
                                    str(match[1][1]), match[0][1]))
                            j = lst2
                            string = str(i) + ":\n\n" + "\n".join(j) + "\r\n\n"
                            lst = dct[message.author.name]
                        now = dt.now().strftime("%d %b, %Y (%H:%M:%S)")
                        with open("predict_log.txt", "w") as f:
                            f.write(now + "\n" + string + string1)
                    except:
                        pass
                    if dump == True:
                        with open("predict_matches.dat", "wb") as f:
                            pickle.dump(predict_dct, f)

            if reaction.emoji == "2️⃣":
                g = open("predict_matches.dat", "rb")
                predict_dct = pickle.load(g)
                matches = predict_dct["Matches"]
                dct = predict_dct["Predictions"]
                g.close()
                lst = dct.get(message.author.name, [])
                if lst == []:
                    pass
                else:
                    string1 = ""
                    for match in lst:
                        string1 = string1 + ("{} {}-{} {}".format(
                            match[0][0], str(match[1][0]), str(match[1][1]),
                            match[0][1])) + "\n"
                    embed = discord.Embed(title="Your Current Predictions",
                                          description="\n\n" + string1,
                                          color=0x4cfa11)
                    await message.channel.send(
                        "(yes/no) Do you want to change your current predictions? (Previous prediction will be deleted after entering yes)",
                        embed=embed)
                    try:
                        msg = await client.wait_for('message',
                                                    check=check1,
                                                    timeout=20)
                    except asyncio.TimeoutError:
                        await message.channel.send("Timeout")
                        return
                    if msg.content.lower() in ("y", "yes"):
                        pass
                    else:
                        await message.channel.send("Cancelled")
                        return
                dct[message.author.name] = []
                for match in matches:
                    await message.channel.send(
                        message.author.mention +
                        " Enter score for {} vs {}. Example format- **1-2**".
                        format(match[0], match[1]))
                    try:
                        msg = await client.wait_for('message',
                                                    check=check1,
                                                    timeout=30)
                        score = msg.content
                        try:
                            sc1 = int(score[:score.index("-")])
                            sc2 = int(score[score.index("-") + 1:])
                            dct[message.author.name].append([(match[0],
                                                              match[1]),
                                                             (sc1, sc2)])
                        except ValueError:
                            await message.channel.send("Wrong format")
                            break
                    except asyncio.TimeoutError:
                        await message.channel.send("Time's up, Try again")
                        break
                else:
                    await message.channel.send("Done!")
                with open("predict_matches.dat", "wb") as f:
                    pickle.dump(predict_dct, f)
                try:
                    with open("predict_matches.dat", "rb") as f:
                        dct = pickle.load(f)["Predictions"]
                    lst = dct[message.author.name]
                    string1 = ""
                    for match in lst:
                        string1 = string1 + ("{} {}-{} {}".format(
                            match[0][0], str(match[1][0]), str(match[1][1]),
                            match[0][1])) + "\n"
                except KeyError:
                    string = "Sorry, no predictions available"
                embed = discord.Embed(title="Your Current Predictions",
                                      description="\n\n" + string1,
                                      color=0x4cfa11)
                await message.channel.send(embed=embed)

            if reaction.emoji == "3️⃣":
                for role in user.roles:
                    if u"President" in role.name or u"Referee" in role.name:
                        flag = 1
                if flag == 0:
                    try:
                        with open("predict_matches.dat", "rb") as f:
                            dct = pickle.load(f)["Predictions"]
                        lst = dct[message.author.name]
                        string1 = ""
                        for match in lst:
                            string1 = string1 + ("{} {}-{} {}".format(
                                match[0][0], str(match[1][0]), str(
                                    match[1][1]), match[0][1])) + "\n"
                    except KeyError:
                        string = "Sorry, no predictions available"
                    embed = discord.Embed(title="Your Current Predictions",
                                          description="\n\n" + string1,
                                          color=0x4cfa11)
                    await message.channel.send(embed=embed)
                elif flag == 1:
                    try:
                        with open("predict_matches.dat", "rb") as f:
                            dct = pickle.load(f)["Predictions"]
                        string = ""
                        for i, j in dct.items():
                            lst2 = []
                            for match in j:
                                lst2.append("{} {}-{} {}".format(
                                    match[0][0], str(match[1][0]),
                                    str(match[1][1]), match[0][1]))
                            j = lst2
                            string = string + str(i) + ":\n\n" + "\n".join(
                                j) + "\n\n"
                            lst = dct[message.author.name]
                        await message.author.send(string)
                    except:
                        string = "Sorry, no predictions available"
                    lst = dct[message.author.name]
                    string1 = ""
                    for match in lst:
                        string1 = string1 + ("{} {}-{} {}".format(
                            match[0][0], str(match[1][0]), str(match[1][1]),
                            match[0][1])) + "\n"
                    embed = discord.Embed(title="Your Current Predictions",
                                          description="\n\n" + string1,
                                          color=0x4cfa11)
                    await message.channel.send(embed=embed)
            if reaction.emoji == "4️⃣":
                for role in user.roles:
                    if u"Referee" in role.name or u"President" in role.name:
                        flag = 1
                if flag == 0:
                    await message.channel.send(
                        "You don't have appropiate roles.")
                elif flag == 1:
                    g = open("predict_matches.dat", "rb")
                    predict_dct = pickle.load(g)
                    matches = predict_dct["Matches"]
                    lst = []
                    g.close()
                    for match in matches:
                        try:
                            await message.channel.send(
                                "Enter result for {} vs {}. Example format- **1-2**"
                                .format(match[0], match[1]))
                            msg = await client.wait_for('message',
                                                        check=check1,
                                                        timeout=30)
                            score = msg.content
                            try:
                                sc1 = int(score[:score.index("-")])
                                sc2 = int(score[score.index("-") + 1:])
                                lst.append([(match[0], match[1]), (sc1, sc2)])
                            except:
                                await message.channel.send(
                                    "Wrong format, Try Again")
                                break
                        except asyncio.TimeoutError:
                            await message.channel.send("Timeout, Try Again")
                            return
                    else:
                        await message.channel.send("Done!")
                        predict_dct["Results"] = lst
                        string1 = ""
                        lst1 = []
                        for i in range(len(lst)):
                            match = lst[i]
                            lst1.append("{} {}-{} {}".format(
                                match[0][0], str(match[1][0]),
                                str(match[1][1]), match[0][1]))
                        string1 = "\n".join(lst1)
                        embed = discord.Embed(title="Results",
                                              description=string1,
                                              color=0x4cfa11)
                        await message.channel.send("Proceed (Yes/No) ?",
                                                   embed=embed)
                        try:
                            msg = await client.wait_for('message',
                                                        check=check1,
                                                        timeout=30)
                            if msg.content.lower() == "yes":
                                result = eval_result(predict_dct)
                                result = sorted(result.items(),
                                                reverse=True,
                                                key=lambda kv: kv[1])
                                string1 = "**Points Table**\n\n"
                                for i, j in result:
                                    string1 = string1 + str(i) + "\t\t" + str(
                                        j) + "\n"
                                await message.channel.send(string1)
                                with open("predict_matches.dat", "wb") as f:
                                    pickle.dump(predict_dct, f)
                            else:
                                await message.channel.send("Try again")
                        except asyncio.TimeoutError:
                            await message.channel.send("Time out!")
                            return

        flag = 0
except discord.errors.HTTPException:
    time.sleep(10)
    print("HTTP Error")
    pass

try:
    client.run(TOKEN)
except:
    print("Too many requests: Restarting")
    os.system("kill 1")
    os.system("python restarter.py")

