import coc
import disnake
import pytz

from disnake.ext import commands
from Dictionaries.emojiDictionary import emojiDictionary
from collections import defaultdict
from CustomClasses.CustomBot import CustomClient
from coc import utils

tiz = pytz.utc
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]

class War_Log(commands.Cog):

    def __init__(self, bot: CustomClient):
        self.bot = bot
        self.bot.coc_client.add_events(self.new_war, self.war_attack)

    '''
    #in case we end up needing it
    @coc.WarEvents.start_time()
    async def new_war(self, old_war: coc.ClanWar, new_war: coc.ClanWar):
        print(f"{old_war.clan.name} vs {old_war.opponent.name}" )
        print(f"{new_war.clan.name} vs {new_war.opponent.name}" )
        if str(old_war.state) == "inWar" and str(new_war.state) == "inWar":
            #new_war if somehow bypasses
            pass
    '''

    @coc.WarEvents.state()
    async def new_war(self, old_war: coc.ClanWar, new_war: coc.ClanWar):
        #store old war
        #self.bot.store_war(old_war)
        #send notif that a new war started
        tracked = self.bot.clan_db.find({"tag": f"{new_war.clan.tag}"})
        limit = await self.bot.clan_db.count_documents(filter={"tag": f"{new_war.clan.tag}"})
        for cc in await tracked.to_list(length=limit):
            try:
                warlog_channel = cc.get("war_log")
                if warlog_channel is None:
                    continue
                try:
                    warlog_channel = await self.bot.fetch_channel(warlog_channel)
                    if warlog_channel is None:
                        continue
                except (disnake.NotFound, disnake.Forbidden):
                    await self.bot.clan_db.update_one({"server": cc.get("server")}, {'$set': {"war_log": None}})
                    continue

                if new_war.state == "preparation":
                    war_state = "In Prep"
                    war_pos = "Starting"
                    war_time = new_war.start_time.time.replace(tzinfo=tiz).timestamp()

                    war_cog = self.bot.get_cog(name="War")
                    th_comps = await war_cog.war_th_comps(new_war)

                    embed = disnake.Embed(description=f"[**{new_war.clan.name}**]({new_war.clan.share_link})",
                                          color=disnake.Color.green())
                    embed.add_field(name=f"**War Against**",
                                    value=f"[**{new_war.opponent.name}**]({new_war.opponent.share_link})\n­\n",
                                    inline=False)
                    embed.add_field(name=f"**War State**",
                                    value=f"{war_state} ({new_war.team_size} vs {new_war.team_size})\n"
                                          f"{war_pos}: <t:{int(war_time)}:R>\n­\n", inline=False)

                    embed.add_field(name="War Composition", value=f"{new_war.clan.name}\n{th_comps[0]}\n"
                                                                  f"{new_war.opponent.name}\n{th_comps[1]}",
                                    inline=False)

                    embed.set_thumbnail(url=new_war.clan.badge.large)
                    embed.set_footer(text=f"{new_war.type.capitalize()} War")
                    await warlog_channel.send(embed=embed)

                if new_war.state == "inWar":
                    embed = disnake.Embed(description=f"[**{new_war.clan.name}**]({new_war.clan.share_link})",
                                          color=disnake.Color.yellow())
                    embed.add_field(name=f"**War Started Against**",
                                    value=f"[**{new_war.opponent.name}**]({new_war.opponent.share_link})\n­",
                                    inline=False)
                    embed.set_thumbnail(url=new_war.clan.badge.large)
                    embed.set_footer(text=f"{new_war.type.capitalize()} War")
                    await warlog_channel.send(embed=embed)

                if new_war.state == "warEnded":
                    war_state = "Ended"
                    war_pos = "War Over"
                    war_time = new_war.end_time.time.replace(tzinfo=tiz).timestamp()

                    war_cog = self.bot.get_cog(name="War")
                    stats = await war_cog.calculate_stars_percent(new_war)
                    if stats[2] > stats[0]:
                        result = "War Won"
                    elif stats[2] == stats[0]:
                        if stats[3] > stats[1]:
                            result = "War Won"
                        else:
                            result = "War Lost"
                    else:
                        result = "War Lost"
                    team_stars = str(stats[2]).ljust(7)
                    opp_stars = str(stats[0]).rjust(7)
                    team_per = (str(stats[3]) + "%").ljust(7)
                    opp_per = (str(stats[1]) + "%").rjust(7)
                    team_hits = f"{len(new_war.attacks) - len(new_war.opponent.attacks)}/{new_war.team_size * new_war.attacks_per_member}".ljust(
                        7)
                    opp_hits = f"{len(new_war.opponent.attacks)}/{new_war.team_size * new_war.attacks_per_member}".rjust(
                        7)

                    embed = disnake.Embed(description=f"[**{new_war.clan.name}**]({new_war.clan.share_link})",
                                          color=disnake.Color.red())
                    embed.add_field(name=f"**War Against**",
                                    value=f"[**{new_war.opponent.name}**]({new_war.opponent.share_link})\n­\n",
                                    inline=False)
                    embed.add_field(name=f"**{result}**",
                                    value=f"{war_state} ({new_war.team_size} vs {new_war.team_size})\n"
                                          f"{war_pos}: <t:{int(war_time)}:R>\n­\n", inline=False)
                    embed.add_field(name="**War Stats**",
                                    value=f"`{team_hits}`<a:swords:944894455633297418>`{opp_hits}`\n"
                                          f"`{team_stars}`<:star:825571962699907152>`{opp_stars}`\n"
                                          f"`{team_per}`<:broken_sword:944896241429540915>`{opp_per}`\n­"
                                    , inline=False)

                    embed.set_thumbnail(url=new_war.clan.badge.large)
                    embed.set_footer(text=f"{new_war.type.capitalize()} War")
                    await warlog_channel.send(embed=embed)
            except:
                continue

    @coc.WarEvents.war_attack()
    async def war_attack(self, attack: coc.WarAttack, war: coc.ClanWar):
        #is an attack
        tracked = self.bot.clan_db.find({"tag": f"{war.clan.tag}"})
        limit = await self.bot.clan_db.count_documents(filter={"tag": f"{war.clan.tag}"})
        for cc in await tracked.to_list(length=limit):
            try:
                warlog_channel = cc.get("war_log")
                if warlog_channel is None:
                    continue
                try:
                    warlog_channel = await self.bot.fetch_channel(warlog_channel)
                    if warlog_channel is None:
                        continue
                except (disnake.NotFound, disnake.Forbidden):
                    await self.bot.clan_db.update_one({"server": cc.get("server")}, {'$set': {"war_log": None}})
                    continue

                star_str = ""
                stars = attack.stars
                for x in range(0, stars):
                    star_str += self.bot.emoji.war_star.emoji_string
                for x in range(0, 3 - stars):
                    star_str += self.bot.emoji.no_star.emoji_string

                if attack.is_fresh_attack:
                    fresh_emoji = self.bot.emoji.yes
                else:
                    fresh_emoji = self.bot.emoji.no
                war_cog = self.bot.get_cog(name="War")
                stats = await war_cog.calculate_stars_percent(war)

                if attack.attacker.clan.tag == war.clan.tag:
                    embed = disnake.Embed(
                        description=f"{emojiDictionary(attack.attacker.town_hall)}[**{attack.attacker.name}**]({attack.attacker.share_link}) {star_str}{attack.destruction}%"
                                    f"\n- Defender: {emojiDictionary(attack.defender.town_hall)}{attack.defender} | {war.opponent.name}\n"
                                    f"- {self.bot.emoji.time}{attack.duration}s | {attack.attacker.town_hall} v {attack.defender.town_hall} | Fresh: {fresh_emoji}",
                        color=disnake.Color.green())
                    embed.set_footer(text=f"{war.clan.name} {stats[2]}-{stats[0]}", icon_url=war.clan.badge.url)
                else:
                    # is a defense
                    embed = disnake.Embed(
                        description=f"{emojiDictionary(attack.attacker.town_hall)}[**{attack.attacker.name}**]({attack.attacker.share_link}) {star_str}{attack.destruction}%"
                                    f"\n- Defender: {emojiDictionary(attack.defender.town_hall)}{attack.defender} | {war.clan.name}\n"
                                    f"- {self.bot.emoji.time}{attack.duration}s | {attack.attacker.town_hall} v {attack.defender.town_hall} | Fresh: {fresh_emoji}",
                        color=disnake.Color.red())
                    embed.set_footer(text=f"{war.opponent.name} {stats[0]}-{stats[2]}", icon_url=war.clan.badge.url)
                await warlog_channel.send(embed=embed)
            except:
                continue


def setup(bot: CustomClient):
    bot.add_cog(War_Log(bot))