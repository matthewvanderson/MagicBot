import coc
import re
import disnake
import pendulum as pend

from collections import defaultdict, namedtuple
from datetime import datetime
from classes.player import ClanCapitalWeek
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from classes.bot import CustomClient
else:
    from disnake.ext.commands import AutoShardedBot as CustomClient
from typing import List
from utility.clash.capital import get_season_raid_weeks
from utility.clash.other import cwl_league_emojis, is_games, league_to_emoji, gen_season_start_end_as_iso, gen_season_start_end_as_timestamp, games_season_start_end_as_timestamp
from utility.discord_utils import register_button
from utility.general import create_superscript, get_guild_icon, smart_convert_seconds
from utility.constants import leagues, item_to_name
from exceptions.CustomExceptions import MessageException
from ..graphs.utils import monthly_bar_graph, daily_graph


@register_button("familycompo", parser="_:server:type")
async def family_composition(bot: CustomClient, server: disnake.Guild, type: str, embed_color: disnake.Color):

    bucket = defaultdict(int)
    clan_tags = await bot.get_guild_clans(guild_id=server.id)
    clans = await bot.get_clans(tags=clan_tags)

    def process_member(member: coc.ClanMember, bucket):
        if type == "Townhall":
            if member._raw_data.get("townHallLevel") == 0:
                return
            bucket[str(member._raw_data.get("townHallLevel"))] += 1
        elif type == "Trophies":
            bucket[str(int(str(member.trophies)[0]) * 1000 if member.trophies >= 1000 else 100)] += 1
        elif type == "Location":
            location = tag_to_location.get(member.tag)
            if location:
                bucket[location] += 1
        elif type == "Role":
            bucket[member.role.in_game_name] += 1
        elif type == "League":
            bucket[member.league.name] += 1

    if type == "Location":
        location_info = await bot.leaderboard_db.find({"tag": {"$in": [m.tag for clan in clans for m in clan.members]}}, {"tag": 1, "country_name": 1, "country_code": 1}).to_list(length=None)
        tag_to_location = {d.get("tag"): d.get("country_name") for d in location_info}
        location_name_to_code = {d.get("country_name"): d.get("country_code") for d in location_info}

    total_count = 0
    for clan in clans:
        for member in clan.members:
            total_count += 1
            process_member(member, bucket)

    formats = {
        "Townhall": "`{value:2}` {icon}`TH{key} `\n",
        "Trophies": "`{value:2}` {icon}`{key}+ Trophies`\n",
        "Location": "`{value:2}` {icon}`{key}`\n",
        "Role": "`{value:2}` {icon}`{key}`\n",
        "League": "`{value:2}` {icon}`{key}`\n",
    }
    footer_text = f"{total_count} accounts"

    def get_icon(type, key):
        if type == "Townhall":
            return bot.fetch_emoji(int(key))
        elif type == "Location":
            return f":flag_{location_name_to_code.get(key).lower()}:"
        elif type == "League":
            return league_to_emoji(key)
        return ""

    text = ""
    field_to_sort = 1
    if type == "Townhall":
        field_to_sort = 0
    for key, value in sorted(bucket.items(), key=lambda x: int(x[field_to_sort]), reverse=True):
        icon = get_icon(type, key)
        text += formats[type].format(key=key, value=value, icon=icon)

    if type == "Townhall":
        total = sum(int(key) * value for key, value in bucket.items())
        footer_text += f' | Avg Townhall: {round((total / total_count), 2)}'

    embed = disnake.Embed(description=text, color=embed_color)
    embed.set_author(name=f"{server.name} {type} Compo", icon_url=get_guild_icon(guild=server))
    embed.set_footer(text=footer_text)
    embed.timestamp = datetime.now()
    return embed


@register_button("familysummary", parser="_:server:season:limit")
async def family_summary(bot: CustomClient, server: disnake.Guild, season: str, limit: int, embed_color: disnake.Color):
    season = bot.gen_season_date() if season is None else season
    member_tags = await bot.get_family_member_tags(guild_id=server.id)
    #we dont want results w/ no name
    results = await bot.player_stats.find({"$and" : [
                                            {"tag" : {"$in": member_tags}},
                                            {"name" : {"$ne" : None}}]}
                                          ).to_list(length=None)
    text = ""
    for option, emoji in zip(["gold", "elixir", "dark_elixir"], [bot.emoji.gold, bot.emoji.elixir, bot.emoji.dark_elixir]):
        top_results = sorted(results, key=lambda x: x.get(option, {}).get(season, 0), reverse=True)[:limit]
        if top_results[0] == 0:
            continue
        for count, result in enumerate(top_results, 1):
            looted = result.get(option, {}).get(season, 0)
            if looted == 0:
                continue
            if count == 1:
                text += f"**{emoji} {option.replace('_', ' ').title()}\n**"
            text += f"`{count:<2} {'{:,}'.format(looted):11} \u200e{result['name']}`\n"
        text += "\n"


    for option, emoji in zip(["activity", "attack_wins", "season_trophies"], [bot.emoji.clock, bot.emoji.wood_swords, bot.emoji.trophy]):
        top_results = sorted(results, key=lambda x: x.get(option, {}).get(season, 0), reverse=True)[:limit]
        if top_results[0] == 0:
            continue
        for count, result in enumerate(top_results, 1):
            looted = result.get(option, {}).get(season, 0)
            if looted == 0:
                continue
            if count == 1:
                text += f"**{emoji} {option.replace('_', ' ').title()}\n**"
            text += f"`{count:<2} {'{:,}'.format(looted):4} \u200e{result['name']}`\n"
        text += "\n"

    first_embed = disnake.Embed(description=text, color=embed_color)
    first_embed.set_author(name=f"{server.name} Season Summary ({season})", icon_url=get_guild_icon(server))
    text = ""

    top_results = sorted(results, key=lambda x: x.get("donations", {}).get(season, {}).get("donated", 0), reverse=True)[:limit]
    text += f"**{bot.emoji.up_green_arrow} Donations\n**"
    for count, result in enumerate(top_results, 1):
        looted = result.get("donations", {}).get(season, {}).get("donated", 0)
        text += f"`{count:<2} {'{:,}'.format(looted):7} \u200e{result['name']}`\n"
    text += "\n"

    top_results = sorted(results, key=lambda x: x.get("donations", {}).get(season, {}).get("received", 0), reverse=True)[:limit]
    text += f"**{bot.emoji.down_red_arrow} Received\n**"
    for count, result in enumerate(top_results, 1):
        looted = result.get("donations", {}).get(season, {}).get("received", 0)
        text += f"`{count:<2} {'{:,}'.format(looted):7} \u200e{result['name']}`\n"
    text += "\n"

    season_raid_weeks = get_season_raid_weeks(season=season)
    def capital_gold_donated(elem):
        cc_results = []
        for week in season_raid_weeks:
            week_result = elem.get("capital_gold", {}).get(week)
            cc_results.append(ClanCapitalWeek(week_result))
        return sum([sum(cap.donated) for cap in cc_results])
    top_capital_donos = sorted(results, key=capital_gold_donated, reverse=True)[:limit]
    text += f"**{bot.emoji.capital_gold} CG Donated\n**"
    for count, result in enumerate(top_capital_donos, 1):
        cg_donated = capital_gold_donated(result)
        text += f"`{count:<2} {'{:,}'.format(cg_donated):7} \u200e{result['name']}`\n"
    text += "\n"

    def capital_gold_raided(elem):
        cc_results = []
        for week in season_raid_weeks:
            week_result = elem.get("capital_gold", {}).get(week)
            cc_results.append(ClanCapitalWeek(week_result))
        return sum([sum(cap.raided) for cap in cc_results])
    top_capital_raided = sorted(results, key=capital_gold_raided, reverse=True)[:limit]
    text += f"**{bot.emoji.capital_gold} CG Raided\n**"
    for count, result in enumerate(top_capital_raided, 1):
        cg_raided = capital_gold_raided(result)
        text += f"`{count:<2} {'{:,}'.format(cg_raided):7} \u200e{result['name']}`\n"
    text += "\n"

    SEASON_START, SEASON_END = gen_season_start_end_as_iso(season=season)
    pipeline = [
        {'$match': {
            "$and" : [
                {'$or': [{'data.clan.members.tag': {'$in': member_tags}},
                        {'data.opponent.members.tag': {'$in': member_tags}}]},
                {"data.preparationStartTime": {"$gte": SEASON_START}}, {"data.preparationStartTime": {"$lte": SEASON_END}},
                {"type" : {"$ne" : "friendly"}}
                ]
            }
        },
        {'$project': {'_id': 0,'uniqueKey': {'$concat': [
                        {'$cond': {
                            'if': {'$lt': ['$data.clan.tag', '$data.opponent.tag']},
                            'then': '$data.clan.tag',
                            'else': '$data.opponent.tag'}},
                        {'$cond': {
                            'if': {'$lt': ['$data.opponent.tag', '$data.clan.tag']},
                            'then': '$data.opponent.tag',
                            'else': '$data.clan.tag'}},
                        '$data.preparationStartTime']},
                      'data': 1}},
        {'$group': {'_id': '$uniqueKey', 'data': {'$first': '$data'}}},
        {'$project': {'members': {'$concatArrays': ['$data.clan.members', '$data.opponent.members']}}},
        {'$unwind': '$members'},
        {"$match" : {"members.tag" : {"$in" : member_tags}}},
        {'$project': {
            '_id': 0,
            'tag': '$members.tag',
            "name" : "$members.name",
            'stars': {
                '$sum': '$members.attacks.stars'}
            }
        },
        {'$group': {
            '_id': '$tag',
            "name" : {"$last" : "$name"},
            'totalStars': {
                '$sum': '$stars'}
            }
        },
        {"$sort" : {"totalStars" : -1}},
        {"$limit" : limit}
    ]
    war_star_results = await bot.clan_war.aggregate(pipeline=pipeline).to_list(length=None)

    if war_star_results:
        text += f"**{bot.emoji.war_star} War Stars\n**"
        for count, result in enumerate(war_star_results, 1):
            text += f"`{count:<2} {'{:,}'.format(result.get('totalStars')):3} \u200e{result.get('name')}`\n"

    second_embed = disnake.Embed(description=text, color=embed_color)
    second_embed.timestamp = pend.now(tz=pend.UTC)
    return [first_embed, second_embed]


@register_button("familyoverview", parser="_:server")
async def family_overview(bot: CustomClient, server: disnake.Guild, embed_color: disnake.Color):
    server = await bot.getch_guild(server.id)
    season = bot.gen_season_date()
    clan_tags = await bot.clan_db.distinct("tag", filter={"server": server.id})
    basic_clans = await bot.basic_clan.find({"tag": {"$in": clan_tags}}).to_list(length=None)

    member_count = sum([c.get("members", 0) for c in basic_clans])
    member_tags = [m.get("tag") for clan in basic_clans for m in clan.get("memberList", [])]
    sixty_mins = pend.now(tz=pend.UTC).subtract(minutes=60)
    last_online_sixty_mins = await bot.player_stats.count_documents({"$and" : [{"tag" : {"$in" : member_tags}}, {"last_online" : {"$gte" : int(sixty_mins.timestamp())}}]})
    description_text = (f"- {server.member_count} Members\n"
                        f"- {len(basic_clans)} Clans, {member_count} Members\n"
                        f"- {last_online_sixty_mins} Online (last hour)\n"
                        f"- Created: {bot.timestamper(unix_time=int(server.created_at.timestamp())).text_date}\n"
                        f"- Owner: {server.owner.display_name}")
    first_embed = disnake.Embed(description=description_text, color=embed_color)
    first_embed.set_author(name=f"{server.name} Overview", icon_url=get_guild_icon(server))

    th_compo_bucket = defaultdict(int)
    total_trophies = 0
    legend_player_count = 0
    for clan in basic_clans:
        for member in clan.get("memberList"):
            if member.get('townhall') != 0:
                th_compo_bucket[member.get("townhall")] += 1
            total_trophies += member.get("trophies")
            if member.get("league") == "Legend League":
                legend_player_count += 1

    clan_stats = await bot.clan_stats.find({"tag" : {"$in" : clan_tags}}, projection={"_id" : 0, "tag" : 1, f"{season}" : 1}).to_list(length=None)
    total_donations = 0
    total_received = 0
    total_de_looted = 0
    total_gold_looted = 0
    total_elix_looted = 0
    total_attack_wins = 0
    total_activity = 0
    for c_stat in clan_stats:
        season_stats = c_stat.get(season, {})
        for _, value in season_stats.items():
            total_donations += value.get("donated", 0)
            total_received += value.get("received", 0)
            total_de_looted += value.get("dark_elixir_looted", 0)
            total_gold_looted += value.get("gold_looted", 0)
            total_elix_looted += value.get("elixir_looted", 0)
            total_attack_wins += value.get("attack_wins", 0)
            total_activity += value.get("activity", 0)

    SEASON_START, SEASON_END = gen_season_start_end_as_iso(season=season)
    wars = await bot.clan_wars.find({"$and" : [
                {'$or': [{'data.clan.tag': {'$in': clan_tags}},
                        {'data.opponent.tag': {'$in': clan_tags}}]},
                {"data.preparationStartTime": {"$gte": SEASON_START}}, {"data.preparationStartTime": {"$lte": SEASON_END}},
                {"type" : {"$ne" : "friendly"}}
                ]
            }, projection={"data.clan.tag" : 1, "data.clan.stars" : 1, "data.opponent.stars" : 1, "data.opponent.tag" : 1}).to_list(length=None)
    total_war_stars = 0
    for war in wars:
        if war.get("data").get("clan").get("tag") in clan_tags:
            total_war_stars += war.get("data").get("clan").get("stars")
        else:
            total_war_stars += war.get("data").get("opponent").get("stars")

    stats_text = (f"```Donations: {total_donations:,}\n"
                  f"Received : {total_received:,}\n"
                  f"War Stars: {total_war_stars:,}\n"
                  #f"Gold: {total_gold_looted:,}\n"
                  #f"Elixir: {total_elix_looted:,}\n"
                  #f"Dark Elixir: {total_de_looted:,}\n"
                  f"Activity: {total_activity:,}\n"
                  f"Attack Wins: {total_attack_wins:,}\n```")
    first_embed.add_field(name="Season Stats", value=stats_text, inline=False)

    top_ten_clans = sorted(basic_clans, key=lambda x: leagues.index(x.get("warLeague", "Unranked")))[:10]
    clan_text = ""
    for clan in top_ten_clans:
        clan_text += f'{cwl_league_emojis(clan.get("warLeague", "Unranked"))}`{clan.get("name"):<15} ({clan.get("members")}/50)`\n'
    first_embed.add_field(name="Top 10 Clans", value=clan_text, inline=False)

    th_comp_string = ""
    count = 0
    for th_level, th_count in sorted(th_compo_bucket.items(), reverse=True):
        th_emoji = bot.fetch_emoji(th_level)
        th_comp_string += f"{th_emoji}`{th_count}` "
        count += 1
        if count % 5 == 0:
            th_comp_string += "\n"
    first_embed.add_field(name="Townhall Compo", value=th_comp_string, inline=False)
    first_embed.timestamp = pend.now(tz=pend.UTC)
    return first_embed


@register_button("familyheroprogress", parser="_:server:season:limit")
async def family_hero_progress(bot: CustomClient, server: disnake.Guild, season: str, limit: int, embed_color: disnake.Color):
    season = season or bot.gen_season_date()
    player_tags = await bot.get_family_member_tags(guild_id=server.id)

    SEASON_START, SEASON_END = gen_season_start_end_as_timestamp(season=season)
    pipeline = [
        {"$match": {"$and": [{"tag": {"$in": player_tags}}, {"type": {"$in": list(coc.enums.HERO_ORDER + coc.enums.PETS_ORDER)}},
                             {"time": {"$gte": SEASON_START}}, {"time": {"$lte": SEASON_END}}]}},
        {"$group": {"_id": {"tag": "$tag", "type": "$type"}, "num": {"$sum": 1}}},
        {"$group": {"_id": "$_id.tag", "hero_counts": {"$push": {"hero_name": "$_id.type", "count": "$num"}}}},
        {"$lookup": {"from": "player_stats", "localField": "_id", "foreignField": "tag", "as": "name"}},
        {"$set": {"name": "$name.name"}}
    ]
    results: List[dict] = await bot.player_history.aggregate(pipeline).to_list(length=None)

    class ItemHolder():
        def __init__(self, data: dict):
            self.tag = data.get("_id")
            self.name = data.get("name")[0] if data.get("name") else "unknown"
            self.king = next((item["count"] for item in data["hero_counts"] if item["hero_name"] == "Barbarian King"), 0)
            self.queen = next((item["count"] for item in data["hero_counts"] if item["hero_name"] == "Archer Queen"), 0)
            self.warden = next((item["count"] for item in data["hero_counts"] if item["hero_name"] == "Grand Warden"), 0)
            self.rc = next((item["count"] for item in data["hero_counts"] if item["hero_name"] == "Royal Champion"), 0)
            self.pets = sum(next((item["count"] for item in data["hero_counts"] if item["hero_name"] == pet), 0) for pet in coc.enums.PETS_ORDER
                            )
            self.total_upgraded = self.king + self.queen + self.warden + self.rc + self.pets

    all_items = []
    for result in results:
        all_items.append(
            ItemHolder(data=result)
        )
    all_items = sorted(all_items, key=lambda x: x.total_upgraded, reverse=True)[:min(limit, len(all_items))]
    if not all_items:
        embed = disnake.Embed(description="**No Upgrades Yet**", colour=disnake.Color.red())
    else:
        text = f"BK AQ WD RC Pet Name          \n"
        for item in all_items:
            text += re.sub(r'\b0\b', "-", f"{item.king:<2} {item.queen:<2} {item.warden:<2} {item.rc:<2} {item.pets:<2}", count=6) + f"  {item.name[:13]}\n"
        embed = disnake.Embed(description=f"```{text}```", colour=embed_color)
    embed.set_author(name=f"{server.name} Hero & Pet Upgrades", icon_url=get_guild_icon(server))

    enums = coc.enums.HERO_ORDER + coc.enums.PETS_ORDER
    pipeline = [
        {"$match": {"$and": [{"tag": {"$in": player_tags}},
                             {"type": {"$in": enums}},
                             {"time": {"$gte": SEASON_START}},
                             {"time": {"$lte": SEASON_END}}]}},
        {"$group": {"_id": {"type": "$type"}, "num": {"$sum": 1}}},
        {"$sort": {"num": -1}},
        {"$limit": 25}
    ]
    results: List[dict] = await bot.player_history.aggregate(pipeline).to_list(length=None)
    text = ""
    total_upgrades = 0
    for result in results:
        type = result.get("_id").get("type")
        emoji = bot.fetch_emoji(type)
        amount = result.get("num")
        total_upgrades += amount
        text += f"{emoji}`{type:15} {amount:3}`\n"

    totals_embed = disnake.Embed(description=f"{text}", colour=embed_color)
    totals_embed.timestamp = pend.now(tz=pend.UTC)
    totals_embed.set_footer(text=f"{season} | {total_upgrades} Upgrades")

    return [embed, totals_embed]


@register_button("familytroopprogress", parser="_:server:season:limit")
async def family_troop_progress(bot: CustomClient, server: disnake.Guild, season: str, limit: int, embed_color: disnake.Color):
    season = season or bot.gen_season_date()

    player_tags = await bot.get_family_member_tags(guild_id=server.id)

    SEASON_START, SEASON_END = gen_season_start_end_as_timestamp(season=season)
    pipeline = [
        {"$match": {"$and": [{"tag": {"$in": player_tags}}, {"type": {"$in": list(coc.enums.HOME_TROOP_ORDER + coc.enums.SPELL_ORDER + coc.enums.BUILDER_TROOPS_ORDER)}},
                             {"time": {"$gte": SEASON_START}}, {"time": {"$lte": SEASON_END}}]}},
        {"$group": {"_id": {"tag": "$tag", "type": "$type"}, "num": {"$sum": 1}}},
        {"$group": {"_id": "$_id.tag", "counts": {"$push": {"name": "$_id.type", "count": "$num"}}}},
        {"$lookup": {"from": "player_stats", "localField": "_id", "foreignField": "tag", "as": "name"}},
        {"$set": {"name": "$name.name"}}
    ]
    results: List[dict] = await bot.player_history.aggregate(pipeline).to_list(length=None)

    class ItemHolder():
        def __init__(self, data: dict):
            self.tag = data.get("_id")
            self.name = data.get("name", ["unknown"])[0]
            self.troops = sum(
                next((item["count"] for item in data["counts"] if item["name"] == troop and troop != "Baby Dragon"), 0) for troop in
                list(set(coc.enums.HOME_TROOP_ORDER) - set(coc.enums.SIEGE_MACHINE_ORDER))
            )
            self.spells = sum(
                next((item["count"] for item in data["counts"] if item["name"] == spell), 0) for spell in coc.enums.SPELL_ORDER
            )
            self.sieges = sum(
                next((item["count"] for item in data["counts"] if item["name"] == siege), 0) for siege in coc.enums.SIEGE_MACHINE_ORDER
            )
            self.builder_troops = sum(
                next((item["count"] for item in data["counts"] if item["name"] == b_troop and b_troop != "Baby Dragon"), 0) for b_troop in coc.enums.BUILDER_TROOPS_ORDER
            )
            self.total_upgraded = self.troops + self.spells + self.sieges + self.builder_troops

    all_items = []
    for result in results:
        all_items.append(
            ItemHolder(data=result)
        )
    all_items = sorted(all_items, key=lambda x: x.total_upgraded, reverse=True)[:min(limit, len(all_items))]
    if not all_items:
        embed = disnake.Embed(description="**No Upgrades Yet**",colour=embed_color)
    else:
        text = f"HT SP SG BT Name          \n"
        for item in all_items:
            text += f"{item.troops:<2} {item.spells:<2} {item.sieges:<2} {item.builder_troops:<2} {item.name[:13]}\n"
        embed = disnake.Embed(description=f"```{text}```", colour=embed_color)
    embed.set_author(name=f"{server.name} Hero & Pet Upgrades", icon_url=get_guild_icon(server))


    enums = coc.enums.HOME_TROOP_ORDER + coc.enums.SPELL_ORDER + coc.enums.BUILDER_TROOPS_ORDER
    pipeline = [
        {"$match": {"$and": [{"tag": {"$in": player_tags}},
                             {"type": {"$in": enums}},
                             {"time": {"$gte": SEASON_START}},
                             {"time": {"$lte": SEASON_END}}]}},
        {"$group": {"_id": {"type": "$type"}, "num": {"$sum": 1}}},
        {"$sort": {"num": -1}},
        {"$limit" : 25},
    ]
    results: List[dict] = await bot.player_history.aggregate(pipeline).to_list(length=None)
    text = ""
    total_upgrades = 0
    for result in results:
        type = result.get("_id").get("type")
        emoji = bot.fetch_emoji(type)
        amount = result.get("num")
        total_upgrades += amount
        text += f"{emoji}`{type:15} {amount:3}`\n"

    totals_embed = disnake.Embed(description=f"{text}", colour=embed_color)
    totals_embed.timestamp = pend.now(tz=pend.UTC)
    totals_embed.set_footer(text=f"{season} | {total_upgrades} Upgrades")


    return [embed, totals_embed]


@register_button("familysorted", parser="_:server:sort_by:limit:townhall")
async def family_sorted(bot: CustomClient, server: disnake.Guild, sort_by: str, townhall: int, limit: int, embed_color: disnake.Color):
    tags = await bot.get_family_member_tags(guild_id=server.id, th_filter=townhall)
    if not tags:
        raise MessageException("No players to sort, try a lighter search filter")
    players: list[coc.Player] = await bot.get_players(tags=tags, custom=False)

    def get_longest(players, attribute):
        longest = 0
        for player in players:
            if "ach_" not in attribute and attribute not in ["season_rank", "heroes"]:
                spot = len(str(player.__getattribute__(sort_by)))
            elif "ach_" in sort_by:
                spot = len(str(player.get_achievement(name=sort_by.split('_')[-1], default_value=0).value))
            elif sort_by == "season_rank":
                def sort_func(a_player):
                    try:
                        a_rank = a_player.legend_statistics.best_season.rank
                    except:
                        return 0

                spot = len(str(sort_func(player))) + 1
            else:
                spot = len(str(sum([hero.level for hero in player.heroes if hero.is_home_base])))
            if spot > longest:
                longest = spot
        return longest

    og_sort = sort_by
    sort_by = item_to_name[sort_by]
    if "ach_" not in sort_by and sort_by not in ["season_rank", "heroes"]:
        attr = players[0].__getattribute__(sort_by)
        if isinstance(attr, str) or isinstance(attr, coc.Role) or isinstance(attr, coc.League):
            players = sorted(players, key=lambda x: str(x.__getattribute__(sort_by)))
        else:
            players = sorted(players, key=lambda x: x.__getattribute__(sort_by), reverse=True)
    elif "ach_" in sort_by:
        players = sorted(players, key=lambda x: x.get_achievement(name=sort_by.split('_')[-1], default_value=0).value,
                         reverse=True)
    elif sort_by == "season_rank":
        def sort_func(a_player):
            try:
                a_rank = a_player.legend_statistics.best_season.rank
                return a_rank
            except:
                return 10000000

        players = sorted(players, key=sort_func, reverse=False)
    else:
        longest = 3
        def sort_func(a_player):
            a_rank = sum([hero.level for hero in a_player.heroes if hero.is_home_base])
            return a_rank

        players = sorted(players, key=sort_func, reverse=True)

    players = players[:limit]
    longest = get_longest(players=players, attribute=sort_by)

    text = ""
    for count, player in enumerate(players, 1):
        if sort_by in ["role", "tag", "heroes", "ach_Friend in Need", "town_hall"]:
            emoji = bot.fetch_emoji(player.town_hall)
        elif sort_by in ["versus_trophies", "versus_attack_wins", "ach_Champion Builder"]:
            emoji = bot.emoji.versus_trophy
        elif sort_by in ["trophies", "ach_Sweet Victory!"]:
            emoji = bot.emoji.trophy
        elif sort_by in ["season_rank"]:
            emoji = bot.emoji.legends_shield
        elif sort_by in ["clan_capital_contributions", "ach_Aggressive Capitalism"]:
            emoji = bot.emoji.capital_gold
        elif sort_by in ["exp_level"]:
            emoji = bot.emoji.xp
        elif sort_by in ["ach_Nice and Tidy"]:
            emoji = bot.emoji.clock
        elif sort_by in ["ach_Heroic Heist"]:
            emoji = bot.emoji.dark_elixir
        elif sort_by in ["ach_War League Legend", "war_stars"]:
            emoji = bot.emoji.war_star
        elif sort_by in ["ach_Conqueror", "attack_wins"]:
            emoji = bot.emoji.thick_sword
        elif sort_by in ["ach_Unbreakable"]:
            emoji = bot.emoji.shield
        elif sort_by in ["ach_Games Champion"]:
            emoji = bot.emoji.clan_games

        spot = f"{count}."
        if "ach_" not in sort_by and sort_by not in ["season_rank", "heroes"]:
            text += f"`{spot:3}`{emoji}`{player.__getattribute__(sort_by):{longest}} {player.name[:15]}`\n"
        elif "ach_" in sort_by:
            text += f"`{spot:3}`{emoji}`{player.get_achievement(name=sort_by.split('_')[-1], default_value=0).value:{longest}} {player.name[:13]}`\n"
        elif sort_by == "season_rank":
            try:
                rank = player.legend_statistics.best_season.rank
            except:
                rank = " N/A"
            text += f"`{spot:3}`{emoji}`#{rank:<{longest}} {player.name[:15]}`\n"
        else:
            cum_heroes = sum([hero.level for hero in player.heroes if hero.is_home_base])
            text += f"`{spot:3}`{emoji}`{cum_heroes:3} {player.name[:15]}`\n"

    embed = disnake.Embed(title=f"{server.name} sorted by {og_sort}", description=text, color=embed_color)
    embed.timestamp = pend.now(tz=pend.UTC)
    return embed


@register_button("familydonos", parser="_:server:season:townhall:limit:sort_by:sort_order")
async def family_donations(bot: CustomClient, server: disnake.Guild, season: str, sort_by: str, sort_order: str, townhall: int, limit: int, embed_color: disnake.Color):
    season = bot.gen_season_date() if season is None else season

    family_clan_tags = await bot.clan_db.distinct("tag", filter={"server": server.id})
    family_clan_donations = await bot.clan_stats.find({"tag" : {"$in" : family_clan_tags}}, projection={"_id" : 0, f"{season}" : 1}).to_list(length=None)

    holder = namedtuple("holder", ["tag", "donations", "received"])
    hold_items = []
    for clan_stats in family_clan_donations:
        season_stats = clan_stats.get(season)
        for tag, data in season_stats.items():
            hold_items.append(holder(tag=tag,
                                     donations= data.get("donated", 0),
                                     received= data.get("received", 0)))

    hold_items.sort(key=lambda x: x.__getattribute__(sort_by.lower()), reverse=(sort_order.lower() == "descending"))
    if len(hold_items) == 0:
        raise MessageException("No players, try a lighter search filter")

    tags = [h.tag for h in hold_items[:limit]]
    players = await bot.get_players(tags=tags, custom=True, use_cache=True, fake_results=True)
    map_player = {p.tag: p for p in players}

    text = "` #  DON   REC  NAME        `\n"
    total_donated = 0
    total_received = 0
    for count, member in enumerate(hold_items, 1):
        if count <= limit:
            player = map_player.get(member.tag)
            text += f"`{count:2} {member.donations:5} {member.received:5} {player.clear_name[:13]:13}`[{create_superscript(player.town_hall)}]({player.share_link})\n"
        total_donated += member.donations
        total_received += member.received

    embed = disnake.Embed(description=f"{text}", color=embed_color)
    embed.set_author(name=f"{server.name} Top {min(limit, len(hold_items))} Donators", icon_url=get_guild_icon(server))
    embed.set_footer(icon_url=bot.emoji.clan_castle.partial_emoji.url,
                     text=f"▲{total_donated:,} | ▼{total_received:,} | {season}")
    embed.timestamp = pend.now(tz=pend.UTC)
    graph, _ = await monthly_bar_graph(bot=bot, clan_tags=family_clan_tags, attribute="donations", season=season, html=False)
    embed.set_image(file=graph)
    return embed


@register_button("familygames", parser="_:server:season:sort_by:sort_order:limit")
async def family_clan_games(bot: CustomClient, server: disnake.Guild, season: str, sort_by: str, sort_order: str, limit: int, embed_color: disnake.Color):
    season = season or bot.gen_games_season()
    family_clan_tags = await bot.clan_db.distinct("tag", filter={"server": server.id})

    family_games_stats = await bot.clan_stats.find({"tag" : {"$in" : family_clan_tags}}, projection={"tag" : 1, f"{season}": 1,  "_id" : 0}).to_list(length=None)
    all_member_tags = [tag for clan in family_games_stats for tag in clan.get(season, {}).keys()]
    SEASON_START, SEASON_END = games_season_start_end_as_timestamp(season=season)
    pipeline = [
        {"$match": {"$and": [{"tag": {"$in": all_member_tags}}, {"type": "Games Champion"},
                             {"time": {"$gte": SEASON_START}},
                             {"time": {"$lte": SEASON_END}}]}},
        {"$sort": {"tag": 1, "time": 1}},
        {"$group": {"_id": "$tag", "first": {"$first": "$time"}, "last": {"$last": "$time"}}}
    ]
    results: List[dict] = await bot.player_history.aggregate(pipeline).to_list(length=None)
    # map to a dict
    member_time_dict = {m["_id"]: {"first": m["first"], "last": m["last"]} for m in results}

    holder = namedtuple("holder", ["tag", "points", "time"])
    hold_items = []
    for clan_stats in family_games_stats:
        season_data = clan_stats.get(season, {})
        for tag, data in season_data.items():
            points = data.get("clan_games", 0)
            if points is None:
                points = 0
            time_stats = member_time_dict.get(tag)
            seconds_taken = 9999999999
            if time_stats:
                if points < 4000 and is_games():
                    time_stats["last"] = int(pend.now(tz=pend.UTC).timestamp())
                first_time = pend.from_timestamp(time_stats["first"], tz=pend.UTC)
                last_time = pend.from_timestamp(time_stats["last"], tz=pend.UTC)
                seconds_taken = (last_time - first_time).total_seconds()
            hold_items.append(holder(tag=tag,
                                     points=points,
                                     time=seconds_taken))


    hold_items.sort(key=lambda x: x.__getattribute__(sort_by.lower()), reverse=(sort_order.lower() == "descending"))
    if len(hold_items) == 0:
        raise MessageException("No players, try a lighter search filter")

    tags = [h.tag for h in hold_items[:limit]]
    players = await bot.get_players(tags=tags, custom=True, use_cache=True, fake_results=True)
    map_player = {p.tag: p for p in players}

    text = "` #      TIME    NAME       `\n"
    total_points = 0
    for count, member in enumerate(hold_items, 1):
        if count <= limit:
            time_text = ""
            if member.time != 9999999999:
                time_text = smart_convert_seconds(seconds=member.time, granularity=2)
            player = map_player.get(member.tag)
            text += f"`{count:2} {member.points:4} {time_text:7} {player.clear_name[:13]:13}`[{create_superscript(player.town_hall)}]({player.share_link})\n"
        total_points += member.points

    embed = disnake.Embed(description=f"{text}", color=embed_color)
    embed.set_author(name=f"{server.name} {min(limit, len(hold_items))} Clan Games", icon_url=get_guild_icon(server))
    embed.set_footer(text=f"Total: {total_points:,} | {season}")
    embed.timestamp = pend.now(tz=pend.UTC)
    return embed


@register_button("familyactivity", parser="_:server:season:limit:sort_by:sort_order")
async def family_activity(bot: CustomClient, server: disnake.Guild, season: str, limit: int, sort_by: str, sort_order: str, embed_color: disnake.Color):
    season = season or bot.gen_season_date()
    show_last_online = (bot.gen_season_date() == season)
    family_clan_tags = await bot.clan_db.distinct("tag", filter={"server": server.id})
    clan_stats = await bot.clan_stats.find({"tag" : {"$in" : family_clan_tags}}, projection={"tag" : 1, f"{season}": 1,  "_id" : 0}).to_list(length=None)
    all_member_tags = [tag for clan in clan_stats for tag in clan.get(season, {}).keys()]
    players = await bot.get_players(tags=all_member_tags, custom=True, use_cache=True)
    map_player = {p.tag: p for p in players}


    holder = namedtuple("holder", ["player", "activity", "lastonline"])
    hold_items = []
    for clan_stat in clan_stats:
        season_stats = clan_stat.get(season, {})
        for tag, data in season_stats.items():
            player = map_player.get(tag)
            if player is None:
                continue
            hold_items.append(holder(player=player,
                                     activity=data.get("activity", 0),
                                     lastonline=player.last_online)
                              )

    hold_items.sort(key=lambda x: x.__getattribute__(sort_by), reverse=(sort_order.lower() == "descending"))
    if len(hold_items) == 0:
        raise MessageException("No players, try a lighter search filter")

    if show_last_online:
        text = "` # ACT   LO    NAME        `\n"
    else:
        text = "` #  ACT    NAME        `\n"

    now = int((pend.now(tz=pend.UTC).timestamp()))
    total_activity = 0
    for count, member in enumerate(hold_items, 1):
        if count <= limit:
            if show_last_online:
                time_text = smart_convert_seconds(seconds=(now-member.player.last_online))
                text += f"`{count:2} {member.activity:3} {time_text:7} {member.player.clear_name[:13]:13}`[{create_superscript(member.player.town_hall)}]({member.player.share_link})\n"
            else:
                text += f"`{count:2} {member.activity:4} {member.player.clear_name[:13]:13}`[{create_superscript(member.player.town_hall)}]({member.player.share_link})\n"
        total_activity += member.activity

    embed = disnake.Embed(description=f"{text}", color=embed_color)
    embed.set_author(name=f"{server.name} Top {min(limit, len(hold_items))} Activity", icon_url=get_guild_icon(server))
    embed.set_footer(icon_url=bot.emoji.clock.partial_emoji.url,
                     text=f"Total Activity: {total_activity} | {season}")
    month = bot.gen_season_date(seasons_ago=24, as_text=False).index(season)
    graph, _ = await daily_graph(bot=bot, clan_tags=family_clan_tags, attribute="activity", months=month + 1)
    embed.set_image(file=graph)
    embed.timestamp = pend.now(tz=pend.UTC)
    return embed