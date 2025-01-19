import motor.motor_asyncio
from main import config  # Still cursed but works


class MongoClient:
    looper_db = motor.motor_asyncio.AsyncIOMotorClient(
        config.stats_mongodb, compressors='snappy' if config.is_main else 'zlib'
    )
    db_client = motor.motor_asyncio.AsyncIOMotorClient(
        config.static_mongodb, compressors='snappy' if config.is_main else 'zlib'
    )

    # Databases
    new_looper = looper_db.get_database('new_looper')
    stats = looper_db.get_database('stats')
    cache = looper_db.get_database('cache')
    looper = looper_db.get_database('looper')
    clashking = looper_db.get_database('clashking')
    bot_settings = db_client.get_database('usafam')

    # Collections (Looper)
    history_db = looper.get_collection('legend_history')
    warhits = looper.get_collection('warhits')
    webhook_message_db = looper.get_collection('webhook_messages')
    cwl_db = looper.get_collection('cwl_db')
    clan_wars = looper.get_collection('clan_war')
    command_stats = new_looper.get_collection('command_stats')
    player_history = new_looper.get_collection('player_history')
    clan_history = new_looper.get_collection('clan_history')
    clan_cache = new_looper.get_collection('clan_cache')
    war_elo = looper.get_collection('war_elo')
    raid_weekend_db = looper.get_collection('raid_weekends')
    clan_join_leave = looper.get_collection('join_leave_history')
    base_stats = looper.get_collection('base_stats')
    cwl_groups = looper.get_collection('cwl_group')
    basic_clan = looper.get_collection('clan_tags')
    war_timers = looper.get_collection('war_timer')

    # Collections (ClashKing)
    excel_templates = clashking.get_collection('excel_templates')
    giveaways = clashking.get_collection('giveaways')
    tokens_db = clashking.get_collection('tokens')
    lineups = clashking.get_collection('lineups')
    bot_sync = clashking.get_collection('bot_sync')
    bot_stats = clashking.get_collection('bot_stats')
    autoboards = clashking.get_collection('autoboards')
    number_emojis = clashking.get_collection('number_emojis')

    # Collections (Stats & New Looper)
    base_player = stats.get_collection('base_player')
    legends_stats = stats.get_collection('legends_stats')
    season_stats = stats.get_collection('season_stats')
    capital_cache = cache.get_collection('capital_raids')
    player_stats = new_looper.get_collection('player_stats')
    leaderboard_db = new_looper.get_collection('leaderboard_db')
    clan_leaderboard_db = new_looper.get_collection('clan_leaderboard_db')
    clan_stats = new_looper.get_collection('clan_stats')
    legend_rankings = new_looper.get_collection('legend_rankings')

    # Collections (Bot Settings)
    clan_db = bot_settings.get_collection('clans')
    banlist = bot_settings.get_collection('banlist')
    server_db = bot_settings.get_collection('server')
    profile_db = bot_settings.get_collection('profile_db')
    ignored_roles = bot_settings.get_collection('evalignore')
    general_family_roles = bot_settings.get_collection('generalrole')
    family_exclusive_roles = bot_settings.get_collection('familyexclusiveroles')
    family_position_roles = bot_settings.get_collection('family_roles')
    not_family_roles = bot_settings.get_collection('linkrole')
    townhall_roles = bot_settings.get_collection('townhallroles')
    builderhall_roles = bot_settings.get_collection('builderhallroles')
    legendleague_roles = bot_settings.get_collection('legendleagueroles')
    builderleague_roles = bot_settings.get_collection('builderleagueroles')
    donation_roles = bot_settings.get_collection('donationroles')
    achievement_roles = bot_settings.get_collection('achievementroles')
    status_roles = bot_settings.get_collection('statusroles')
    welcome = bot_settings.get_collection('welcome')
    button_db = bot_settings.get_collection('button_db')
    legend_profile = bot_settings.get_collection('legend_profile')
    youtube_channels = bot_settings.get_collection('youtube_channels')
    reminders = bot_settings.get_collection('reminders')
    whitelist = bot_settings.get_collection('whitelist')
    rosters = bot_settings.get_collection('rosters')
    credentials = bot_settings.get_collection('credentials')
    global_chat_db = bot_settings.get_collection('global_chats')
    global_reports = bot_settings.get_collection('reports')
    strike_list = bot_settings.get_collection('strikes')

    custom_bots = bot_settings.get_collection('custom_bots')
    suggestions = bot_settings.get_collection('suggestions')

    personal_reminders = bot_settings.get_collection('personal_reminders')
    tickets = bot_settings.get_collection('tickets')
    open_tickets = bot_settings.get_collection('open_tickets')
    custom_embeds = bot_settings.get_collection('custom_embeds')
    custom_commands = bot_settings.get_collection('custom_commands')
    bases = bot_settings.get_collection('bases')
    colors = bot_settings.get_collection('colors')
    level_cards = bot_settings.get_collection('level_cards')
    autostrikes = bot_settings.get_collection('autostrikes')
    user_settings = bot_settings.get_collection('user_settings')
    custom_boards = bot_settings.get_collection('custom_boards')
    trials = bot_settings.get_collection('trials')
    autoboard_db = bot_settings.get_collection('autoboard_db')
    player_search = bot_settings.get_collection('player_search')
