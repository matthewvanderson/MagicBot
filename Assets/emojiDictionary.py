def emojiDictionary(emojiName):
    switcher = {
        "Barbarian King": "<:BarbarianKing:1125780508190720041>",
        "Archer Queen": "<:ArcherQueen:1125780510485004399>",
        "Grand Warden": "<:GrandWarden:1125780512699592725>",
        "Royal Champion": "<:RoyalChampion:1125780514486353983>",
        "Battle Copter": "<:battle_copter:1109716293696888852>",
        "Electrofire Wizard": "<:electro_wiz:1109716130735587358>",
        "Archer": "<:Archer:1125780518433206302>",
        "Baby Dragon": "<:BabyDragon:1125780520991731723>",
        "Barbarian": "<:Barbarian:1125780523495731271>",
        "Bowler": "<:Bowler:1125780525102149723>",
        "Electro Dragon": "<:ElectroDragon:1125780527052505128>",
        "Dragon": "<:Dragon:1125780530445693059>",
        "Dragon Rider": "<:dragon_rider:1125780532840644669>",
        "Balloon": "<:Balloon:1125780535801806858>",
        "Ice Golem": "<:IceGolem:1125780538955939920>",
        "Miner": "<:Miner:1125780541090840586>",
        "Hog Rider": "<:HogRider:1125780543473205318>",
        "Yeti": "<:Yeti:1125780545981403226>",
        "Wizard": "<:Wizard:1125780548154040361>",
        "Healer": "<:Healer:1125780550569951453>",
        "Giant": "<:Giant:1125780552419659806>",
        "Goblin": "<:Goblin:1125780554537762897>",
        "Witch": "<:Witch:1125780557029187594>",
        "Minion": "<:Minion:1125780559830986752>",
        "P.E.K.K.A": "<:PEKKA:1125780562586640464>",
        "Wall Breaker": "<:WallBreaker:1125780564667011144>",
        "Golem": "<:Golem:1125780566508314624>",
        "Lava Hound": "<:LavaHound:1125780568559333376>",
        "Valkyrie": "<:Valkyrie:1125780570601947178>",
        "Headhunter": "<:Headhunter:1125780573588299896>",
        "Super Wall Breaker": "<:SuperWallBreaker:1125780575945494579>",
        "Super Barbarian": "<:SuperBarbarian:1125780578139111516>",
        "Super Archer": "<:SuperArcher:1125780580462759987>",
        "Super Giant": "<:SuperGiant:1125780587253334028>",
        "Sneaky Goblin": "<:SneakyGoblin:1125780589824462848>",
        "Rocket Balloon": "<:RocketBalloon:1125780591925792888>",
        "Super Wizard": "<:SuperWizard:1125780593817440267>",
        "Super Miner": "<:sminer:1051845657910071346>",
        "Inferno Dragon": "<:InfernoDragon:1125780596145258639>",
        "Super Minion": "<:SuperMinion:1125780598749941800>",
        "Super Valkyrie": "<:SuperValkyrie:1125780601530753124>",
        "Super Witch": "<:SuperWitch:1125780607239204885>",
        "Ice Hound": "<:IceHound:1125780609290227722>",
        "Super Dragon": "<:SuperDragon:1125780611240579105>",
        "Super Bowler": "<:SuperBowler:1125780613174136852>",
        "Unicorn": "<:Unicorn:1125780616395378808>",
        "Mighty Yak": "<:MightyYak:1125780619079729282>",
        "Electro Owl": "<:ElectroOwl:1125780621474660383>",
        "L.A.S.S.I": "<:LASSI:1125780623605387344>",
        "trophy": "<:trophyy:1125780625778016277>",
        "Wall Wrecker": "<:WallWrecker:1125780628328153129>",
        "Battle Blimp": "<:BattleBlimp:1125780630463057991>",
        "Stone Slammer": "<:StoneSlammer:1125780633055133706>",
        "Siege Barracks": "<:SiegeBarracks:1125795608788226109>",
        "Log Launcher": "<:LogLauncher:1125795611925549097>",
        "Flame Flinger": "<:FlameFlinger:1125795614261776484>",
        "Skeleton Spell": "<:skel:1125795616698667051>",
        "Rage Spell": "<:rs:1125795619831812096>",
        "Poison Spell": "<:ps:1125795621895405598>",
        "Healing Spell": "<:hs:1125795624319717426>",
        "Invisibility Spell": "<:invi:1125795629516476518>",
        "Jump Spell": "<:js:1125795631936573450>",
        "Lightning Spell": "<:ls:1125795633907904512>",
        "Haste Spell": "<:haste:1125795636181213325>",
        "Freeze Spell": "<:fs:1125795638907502602>",
        "Earthquake Spell": "<:es:1125795641654788256>",
        "Bat Spell": "<:bat:1125795643689025606>",
        "Clone Spell": "<:cs:1125795645958144162>",
        "clan castle": "<:clan_castle:1125795648462147594>",
        "shield": "<:clash:1125795651280699392>",
        "Electro Titan": "<:ElectroTitan:1029213693021519963>",
        "Battle Drill": "<:BattleDrill:1029199490038628442>",
        "Recall Spell": "<:recall:1029199491385012304>",
        "Frosty": "<:Frosty:1029199487849201785>",
        "Poison Lizard": "<:PoisonLizard:1029199485450068029>",
        "Phoenix": "<:Phoenix:1029199486347661343>",
        "Diggy": "<:Diggy:1029199488906170428>",
        "Root Rider" : "<:RootRider:1183561929864794222>",
        "Spirit Fox" : "<:PhaseFennec:1183561928438718494>",
        1: "<:02:1125807195456536677>",
        2: "<:02:1125807195456536677>",
        3: "<:03:1125807197415288923>",
        4: "<:04:1125807199495667743>",
        5: "<:05:1125807201752195153>",
        6: "<:06:1125807203803213954>",
        7: "<:07:1125807205757751397>",
        8: "<:08:1125810709406679081>",
        9: "<:09:1125810712078454854>",
        10: "<:10:1125810714179817604>",
        11: "<:11:1125810716608303244>",
        12: "<:12:1125810719259115631>",
        13: "<:132:1125810721490473091>",
        14: "<:14:1125810723822506015>",
        15: "<:th15_big:1029215029486157855>",
        16: "<:16:1183533663367987252>",

        "Barbarian Puppet" : "<:BarbDoll:1183561776642662420>",
        "Rage Vial" : "<:RageVial:1183561869282258984>",
        "Archer Puppet" : "<:ArcherDoll:1183561721445625937>",
        "Invisibility Vial" : "<:InvisVial:1183561773715038239>",
        "Eternal Tome" : "<:EternalTome:1183561873501716610>",
        "Life Gem" : "<:HealGem:1183561875254951936>",
        "Seeking Shield" : "<:SeekingShield:1183561926781976646>",
        "Royal Gem" : "<:LifeGem:1183561925284605972>",
        "Earthquake Boots" : "<:StompBoots:1183561871127744523>",
        "Vampstache" : "<:VampStache:1183561872159539250>",
        "Giant Gauntlet" : "<:GiantGauntlet:1183561778739822632>",
        "Giant Arrow" : "<:MagicArrow:1183561775124324452>",
        "Healer Puppet" : "<:HealerDoll:1183561771588530298>",
        "Rage Gem" : "<:RageGem:1183561924064051343>",
        "Healing Tome" : "<:HeartTome:1183561922319229009>",
        "Freeze Arrow" : "<:FreezeArrow:1183561723500834846>",
        
        "Capital Gold": "<:capitalgold:1125795653696626860>",
        "Capital_Hall7": "<:CH7:1125795655646986291>",
        "District_Hall4": "<:DH4:1125795658629128213>",
        "District_Hall5": "<:DH5:1125795660650786906>",
        "District_Hall3": "<:DH3:1125795662919893032>",
        "District_Hall2": "<:DH2:1125795665549738059>",
        "District_Hall1": "<:DH1:1125795668145999882>",
        "Capital_Hall9": "<:CH9:1125795670310277223>",
        "Capital_Hall10": "<:CH10:1125795672906530887>",
        "Capital_Hall8": "<:CH8:1125795675825774652>",
        "Capital_Hall6": "<:CH6:1125795678061342791>",
        "Capital_Hall4": "<:CH4:1125795680359829545>",
        "Capital_Hall5": "<:CH5:1125795682331144192>",
        "Capital_Hall3": "<:CH3:1125795684176633878>",
        "Capital_Hall2": "<:CH2:1125795686139576340>",
        "Capital_Hall1": "<:CH1:1125795688802951270>",
        "Bomber": "<:Bomber:1125800091161202750>",
        "Hog Glider": "<:HogGlider:1125799777020424223>",
        "Cannon Cart": "<:CannonCart:1125800093753298985>",
        "Power P.E.K.K.A": "<:SuperPEKKA:1125800096072732812>",
        "Boxer Giant": "<:BoxerGiant:1125800098912272455>",
        "Drop Ship": "<:DropShip:1125800101491781702>",
        "Beta Minion": "<:BetaMinion:1125800103974801429>",
        "Raged Barbarian": "<:RagedBarbarian:1125800107116339273>",
        "Night Witch": "<:NightWitch:1125800110111076454>",
        "Sneaky Archer": "<:SneakyArcher:1125800112480854156>",
        "Battle Machine": "<:bm:1041499330240053352>",
        "Super Hog Rider": "<:SHogRider:1120604618100060180>",
        "Apprentice Warden": "<:Apprentice:1120604620713107507>"
    }

    return switcher.get(emojiName)


def legend_emojis(emojiName):
    switcher = {
        "legends_shield": "<:legends:881450752109850635>",
        "sword": "<:sword:825589136026501160>",
        "shield": "<:clash:877681427129458739>",
        "Previous Days": "<:cal:989351376146530304>",
        "Legends Overview": "<:list:989351376796680213>",
        "Graph & Stats": "<:graph:989351375349624832>",
        "Legends History": "<:history:989351374087151617>",
        "quick_check": "<:plusminus:989351373608980490>",
        "gear": "<:gear:989351372711399504>",
        "pin": "<:magnify:944914253171810384>",
        "back": "<:back_arrow:989399022156525650>",
        "forward": "<:forward_arrow:989399021602877470>",
        "print": "<:print:989400875766251581>",
        "refresh": "<:refresh:989399023087652864>",
        "trashcan": "<:trashcan:989534332425232464>",
        "alphabet": "<:alphabet:989649421564280872>",
        "start": "<:start:989649420742176818>",
        "blueshield": "<:blueshield:989649418665996321>",
        "bluesword": "<:bluesword:989649419878166558>",
        "bluetrophy": "<:bluetrophy:989649417760018483>",
        6: "<:06:701579365573459988>",
        7: "<:07:701579365598756874>",
        8: "<:08:701579365321801809>",
        9: "<:09:701579365389041767>",
        10: "<:10:701579365661671464>",
        11: "<:11:701579365699551293>",
        12: "<:12:701579365162418188>",
        13: "<:132:704082689816395787>",
        14: "<:14:828991721181806623>",
        15: "<:th15:1028905841589506099>"
    }

    emoji = switcher.get(emojiName, None)
    return emoji
