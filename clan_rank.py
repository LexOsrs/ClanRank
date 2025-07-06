import requests
from enum import Enum
from data.quests import QUESTS
import os
import json
import logging
from datetime import datetime, UTC
from pydantic import BaseModel
from tabulate import tabulate
import argparse

MAX_CLOGS = 1594

logger = logging.getLogger('ClanRank')
logging.basicConfig(level=logging.DEBUG)

class DiaryEnum(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
    ELITE = 3

class RankItem(BaseModel):
    name: str
    possible_points: int
    points: int = 0
    completed: bool = False

    def to_list(self):
        return [
            self.name,
            "✅" if self.completed else "❌",
            self.points,
            self.possible_points
        ]
    
    def complete(self):
        self.completed = True
        self.points = self.possible_points


class Profile():
    def __init__(self, username: str, use_cache: bool = True) -> None:
        self.username = username
        self.join_date = datetime.today().replace(tzinfo=UTC)
        self.load_data(use_cache=use_cache)

        # Initialise all the data
        self.quest_points = RankItem(
            name="Quest Points",
            possible_points=sum(QUESTS.values()),
        )
        self.miniquests = RankItem(
            name="Miniquests Completed",
            possible_points=len([
                quest
                for quest in self.rp_data['quests']
                if quest['type'] == 2 # Miniquest
            ])
        )
        self.rfd = RankItem(
            name="Recipe for Disaster",
            possible_points=50,
        )

        self.monkey_madness_2 = RankItem(
            name="Monkey Madness II",
            possible_points=50,
        )

        self.dragon_slayer_2 = RankItem(
            name="Dragon Slayer II",
            possible_points=100,
        )

        self.song_of_the_elves = RankItem(
            name="Song of the Elves",
            possible_points=50,
        )

        self.a_kingdom_divided = RankItem(
            name="A Kingdom Divided",
            possible_points=50,
        )

        self.desert_treasure_2 = RankItem(
            name="Desert Treasure II",
            possible_points=100,
        )

        self.while_guthix_sleeps = RankItem(
            name="While Guthix Sleeps",
            possible_points=50,
        )

        # Diaries
        self.achievements_completed = RankItem(
            name="Achievement Diaries Completed",
            possible_points=sum([
                tier['tasksCount']
                for tier in self.rp_data['achievementDiaryTiers']
            ])
        )

        self.easy_diaries = RankItem(
            name="Easy Diaries",
            possible_points=50,
        )

        self.medium_diaries = RankItem(
            name="Medium Diaries",
            possible_points=50,
        )

        self.hard_diaries = RankItem(
            name="Hard Diaries",
            possible_points=100,
        )

        self.elite_diaries = RankItem(
            name="Elite Diaries",
            possible_points=200,
        )

        # PvM
        self.combat_achievement_points = RankItem(
            name="Combat Achievement Points",
            possible_points=sum([
                tier['id'] * tier['tasksCount']
                for tier in self.rp_data['combatAchievementTiers']
            ])
        )

        self.easy_combat_achievements = RankItem(
            name="Easy Combat Achievements",
            possible_points=50,
        )

        self.medium_combat_achievements = RankItem(
            name="Medium Combat Achievements",
            possible_points=50,
        )

        self.hard_combat_achievements = RankItem(
            name="Hard Combat Achievements",
            possible_points=100,
        )   

        self.elite_combat_achievements = RankItem(
            name="Elite Combat Achievements",
            possible_points=100,
        )

        self.master_combat_achievements = RankItem(
            name="Master Combat Achievements",
            possible_points=200,
        )

        self.grandmaster_combat_achievements = RankItem(
            name="Grandmaster Combat Achievements",
            possible_points=300,
        )

        self.dragon_defender = RankItem(
            name="Dragon Defender",
            possible_points=50,
        )

        self.fighter_torso = RankItem(
            name="Fighter Torso",
            possible_points=50,
        )   

        self.fire_cape = RankItem(
            name="Fire Cape",
            possible_points=100,
        )

        self.imbued_god_cape = RankItem(
            name="Imbued God Cape",
            possible_points=50,
        )

        self.vorkaths_head = RankItem(
            name="Vorkath's Head",
            possible_points=50,
        )

        self.gauntlet_cape = RankItem(
            name="Gauntlet Cape",
            possible_points=50,
        )

        self.thread_of_elidinis = RankItem(
            name="Thread of Elidinis",
            possible_points=50,
        )

        self.masori_crafting_kit = RankItem(
            name="Masori Crafting Kit",
            possible_points=25,
        )

        self.menaphite_ornament_kit = RankItem(
            name="Menaphite Ornament Kit",
            possible_points=25,
        )

        self.cursed_phalanx = RankItem(
            name="Cursed Phalanx",
            possible_points=50,
        )

        self.toa_remnants = RankItem(
            name="ToA Remnants",
            possible_points=200,
        )

        self.xerics_guard = RankItem(
            name="Xeric's Guard",
            possible_points=200,
        )

        self.sinhaza_shroud = RankItem(
            name="Sinhaza Shroud",
            possible_points=200,
        )

        self.icthlarins_shroud = RankItem(
            name="Icthlarin's Shroud",
            possible_points=200,
        )   

        self.infernal_cape = RankItem(
            name="Infernal Cape",
            possible_points=200,
        )

        self.dizanas_quiver = RankItem(
            name="Dizana's Quiver",
            possible_points=200,
        )

        self.ancient_blood_ornament_kit = RankItem(
            name="Ancient Blood Ornament Kit",
            possible_points=300,
        )

        self.purifying_sigil = RankItem(
            name="Purifying Sigil",
            possible_points=300,
        )

        self.ehb = RankItem(
            name="EHB",
            possible_points=1250,
        )

        # Skilling
        self.level_1250 = RankItem(
            name="1250 Total Level",
            possible_points=100,
        )

        self.level_1500 = RankItem(
            name="1500 Total Level",
            possible_points=100,
        )   

        self.level_1750 = RankItem(
            name="1750 Total Level",
            possible_points=100,
        )

        self.level_2000 = RankItem(
            name="2000 Total Level",
            possible_points=200,
        )

        self.level_2100 = RankItem(
            name="2100 Total Level",
            possible_points=200,
        )

        self.level_2200 = RankItem(
            name="2200 Total Level",
            possible_points=250,
        )

        self.level_2277 = RankItem(
            name="2277 Total Level",
            possible_points=300,
        )

        self.ehp = RankItem(
            name="EHP",
            possible_points=1250,
        )

        # Miscellaneous
        self.clogs = RankItem(
            name="Collections Logged",
            possible_points=MAX_CLOGS,
        )

        self.music_cape = RankItem(
            name="Music Cape",
            possible_points=50,
        )

        self.one_month_in_clan = RankItem(
            name="1 Month in Clan",
            possible_points=30,
        )

        self.three_months_in_clan = RankItem(
            name="3 Months in Clan",
            possible_points=90,
        )

        self.six_months_in_clan = RankItem(
            name="6 Months in Clan",
            possible_points=180,
        )

        self.one_year_in_clan = RankItem(
            name="1 Year in Clan",
            possible_points=360,
        )

        self.two_years_in_clan = RankItem(
            name="2 Years in Clan",
            possible_points=720,
        )

        # Clan points and rank
        self.clan_points = 0
        self.rank = "Helper"


    def print_summary(self):
        print(f"Username: {self.username}")
        print(f"Rank: {self.rank} ({self.clan_points} pts)")
        print(f"Next Rank: {self.next_rank} ({self.points_to_next_rank} pts to go)")
        print()

        display_data = [["Criteria", "Completion", "Points Eearned", "Possible Points"]]

        display_data.append(["Quests"])
        display_data.append(self.quest_points.to_list())
        display_data.append(self.miniquests.to_list())
        display_data.append(self.rfd.to_list())
        display_data.append(self.monkey_madness_2.to_list())
        display_data.append(self.dragon_slayer_2.to_list())
        display_data.append(self.song_of_the_elves.to_list())
        display_data.append(self.a_kingdom_divided.to_list())
        display_data.append(self.desert_treasure_2.to_list())
        display_data.append(self.while_guthix_sleeps.to_list())
        display_data.append([])

        display_data.append(["Diaries"])
        display_data.append(self.achievements_completed.to_list())
        display_data.append(self.easy_diaries.to_list())
        display_data.append(self.medium_diaries.to_list())
        display_data.append(self.hard_diaries.to_list())
        display_data.append(self.elite_diaries.to_list())
        display_data.append([])

        display_data.append(["PvM"])
        display_data.append(self.combat_achievement_points.to_list())
        display_data.append(self.easy_combat_achievements.to_list())
        display_data.append(self.medium_combat_achievements.to_list())
        display_data.append(self.hard_combat_achievements.to_list())
        display_data.append(self.elite_combat_achievements.to_list())
        display_data.append(self.master_combat_achievements.to_list())
        display_data.append(self.grandmaster_combat_achievements.to_list())
        display_data.append(self.dragon_defender.to_list())
        display_data.append(self.fighter_torso.to_list())
        display_data.append(self.fire_cape.to_list())
        display_data.append(self.imbued_god_cape.to_list())
        display_data.append(self.vorkaths_head.to_list())
        display_data.append(self.gauntlet_cape.to_list())
        display_data.append(self.thread_of_elidinis.to_list())
        display_data.append(self.masori_crafting_kit.to_list())
        display_data.append(self.menaphite_ornament_kit.to_list())
        display_data.append(self.cursed_phalanx.to_list())
        display_data.append(self.toa_remnants.to_list())
        display_data.append(self.xerics_guard.to_list())
        display_data.append(self.sinhaza_shroud.to_list())
        display_data.append(self.icthlarins_shroud.to_list())
        display_data.append(self.infernal_cape.to_list())
        display_data.append(self.dizanas_quiver.to_list())
        display_data.append(self.ancient_blood_ornament_kit.to_list())
        display_data.append(self.purifying_sigil.to_list())
        display_data.append(self.ehb.to_list())
        display_data.append([])

        display_data.append(["Skilling"])
        display_data.append(self.level_1250.to_list())
        display_data.append(self.level_1500.to_list())
        display_data.append(self.level_1750.to_list())
        display_data.append(self.level_2000.to_list())
        display_data.append(self.level_2100.to_list())
        display_data.append(self.level_2200.to_list())
        display_data.append(self.level_2277.to_list())
        display_data.append(self.ehp.to_list())
        display_data.append([])

        display_data.append(["Miscellaneous"])
        display_data.append(self.clogs.to_list())
        display_data.append(self.music_cape.to_list())
        display_data.append(self.one_month_in_clan.to_list())
        display_data.append(self.three_months_in_clan.to_list())
        display_data.append(self.six_months_in_clan.to_list())
        display_data.append(self.one_year_in_clan.to_list())
        display_data.append(self.two_years_in_clan.to_list())

        print(tabulate(display_data, headers='firstrow'))


    def load_data(self, use_cache: bool = True):
        if use_cache and os.path.exists('/tmp/rp.json'):
            with open('/tmp/rp.json') as f:
                self.rp_data = json.load(f)
        else:
            rp_data = requests.get(f'https://api.runeprofile.com/profiles/{self.username}').json()

            if rp_data.get('message') == "Account not found.":
                logger.warning("RuneProfile data not found")
                self.rp_data = None
            else:
                self.rp_data = rp_data
                with open('/tmp/rp.json', 'w') as f:
                    json.dump(rp_data, f, indent=2)
        
        if use_cache and os.path.exists('/tmp/wom.json'):
            with open('/tmp/wom.json') as f:
                self.wom_data = json.load(f)
        else:
            wom_data = requests.get(f"https://api.wiseoldman.net/v2/players/{self.username}").json()

            if wom_data.get('message') == "Player not found.":
                logger.warning("Wise Old Man data not found")
                self.wom_data = None
            else:
                self.wom_data = wom_data
                with open('/tmp/wom.json', 'w') as f:
                    json.dump(wom_data, f, indent=2)
        
        
        if use_cache and os.path.exists('/tmp/clan.json'):
            with open('/tmp/clan.json') as f:
                clan_data = json.load(f)
        else:
            clan_data = requests.get("https://api.wiseoldman.net/v2/groups/1169").json()

            with open('/tmp/clan.json', 'w') as f:
                json.dump(clan_data, f, indent=2)
        
        for member in clan_data['memberships']:
            if member['player']['displayName'] == self.username:
                # This isn't accurate but close enough for me
                self.join_date = datetime.fromisoformat(member['createdAt'])


    def is_diary_tier_completed(self, diary_type: DiaryEnum) -> bool:
        achievement_diaries = self.rp_data['achievementDiaryTiers']

        return all(
            [
                diary['completedCount'] == diary['tasksCount']
                for diary in achievement_diaries
                if diary['tierIndex'] == diary_type.value
            ]
        )

    def get_quest_points(self) -> int:
        quests = self.rp_data['quests']

        points = sum([
            QUESTS.get(quest['name'], 0)
            for quest in quests
            if quest['state'] == 2
        ])

        return points

    def get_miniquests_complete(self) -> int:
        quests = self.rp_data['quests']

        points = len([
            quest
            for quest in quests
            if quest['type'] == 2 # Miniquest
            and quest['state'] == 2 # Completed
        ])

        return points

    def set_points_from_specific_quests(self) -> None:
        quests = self.rp_data['quests']

        for quest in quests:
            if quest['state'] == 2:
                match quest['name']:
                    case "Recipe for Disaster":
                        self.rfd.complete()
                    case "Monkey Madness II":
                        self.monkey_madness_2.complete()
                    case "Dragon Slayer II":
                        self.dragon_slayer_2.complete()
                    case "Song of the Elves":
                        self.song_of_the_elves.complete()
                    case "A Kingdom Divided":
                        self.a_kingdom_divided.complete()
                    case "Desert Treasure II - The Fallen Empire":
                        self.desert_treasure_2.complete()
                    case "While Guthix Sleeps":
                        self.while_guthix_sleeps.complete()
                    case _:
                        pass


    def set_combat_achievement_points(self):
        combat_achievements = self.rp_data['combatAchievementTiers']

        self.combat_achievement_points.points = sum([
            tier['completedCount'] * tier['id']
            for tier in combat_achievements
        ])

        cumulative_points = 0
        points_per_tier = []

        for tier in combat_achievements:
            cumulative_points += tier['id'] * tier['tasksCount']
            points_per_tier.append(cumulative_points)
        
        if self.combat_achievement_points.points >= points_per_tier[0]:
            self.easy_combat_achievements.complete()
        
        if self.combat_achievement_points.points >= points_per_tier[1]:
            self.medium_combat_achievements.complete()

        if self.combat_achievement_points.points >= points_per_tier[2]:
            self.hard_combat_achievements.complete()

        if self.combat_achievement_points.points >= points_per_tier[3]:
            self.elite_combat_achievements.complete()

        if self.combat_achievement_points.points >= points_per_tier[4]:
            self.master_combat_achievements.complete()

        if self.combat_achievement_points.points >= points_per_tier[5]:
            self.grandmaster_combat_achievements.complete()


    def set_points_from_specific_items(self) -> None:
        all_items = [item['name'] for item in self.rp_data['items']]

        if "Dragon defender" in all_items:
            self.dragon_defender.complete()   

        if "Fighter torso" in all_items:
            self.fighter_torso.complete()

        if "Fire cape" in all_items:
            self.fire_cape.complete()

        if "Vorkath's head" in all_items:
            self.vorkaths_head.complete()

        if "Gauntlet cape" in all_items:
            self.gauntlet_cape.complete()

        if "Thread of elidinis" in all_items:
            self.thread_of_elidinis.complete()

        if "Masori crafting kit" in all_items:
            self.masori_crafting_kit.complete()

        if "Menaphite ornament kit" in all_items:
            self.menaphite_ornament_kit.complete()

        if "Cursed phalanx" in all_items:
            self.cursed_phalanx.complete()

        if "Xeric's guard" in all_items:
            self.xerics_guard.complete()

        if "Sinhaza shroud tier 1" in all_items:
            self.sinhaza_shroud.complete()

        if "Icthlarin's shroud (tier 1)" in all_items:
            self.icthlarins_shroud.complete()

        if "Infernal cape" in all_items:
            self.infernal_cape.complete()

        if "Dizana's quiver" in all_items:
            self.dizanas_quiver.complete()

                  
        if [quest['state'] == 2 for quest in self.rp_data['quests'] if quest['name'] == "Mage Arena II"]:
            self.imbued_god_cape.complete()
        
        if all([
            item in all_items
            for item in [
                "Remnant of akkha",
                "Remnant of ba-ba",
                "Remnant of kephri",
                "Remnant of zebak",
                "Ancient remnant",
            ]
        ]):
            self.toa_remnants.complete()
        
        # Cannot currently figure out the two ornament kits from available data:
        #  * Ancient blood ornament kit
        #  * Purifying sigil


    def set_item_data(self):
        # Quests
        self.quest_points.points = self.get_quest_points()
        if self.quest_points.points == self.quest_points.possible_points:
            self.quest_points.complete()
        
        self.miniquests.points = self.get_miniquests_complete()
        if self.miniquests.points == self.miniquests.possible_points:
            self.miniquests.complete()

        self.set_points_from_specific_quests()

        # Diaries
        self.achievements_completed.points = sum(
            [tier['completedCount'] for tier in self.rp_data['achievementDiaryTiers']]
        )

        if self.achievements_completed.points == self.achievements_completed.possible_points:
            self.achievements_completed.complete()
            
        if self.is_diary_tier_completed(DiaryEnum.EASY):
            self.easy_diaries.complete()

        if self.is_diary_tier_completed(DiaryEnum.MEDIUM):
            self.medium_diaries.complete()

        if self.is_diary_tier_completed(DiaryEnum.HARD):
            self.hard_diaries.complete()    

        if self.is_diary_tier_completed(DiaryEnum.ELITE):
            self.elite_diaries.complete()
        
        # PvM
        self.set_combat_achievement_points()
        self.set_points_from_specific_items()

        ehb = int(self.wom_data['ehb'])
        if ehb >= 1250:
            self.ehb.complete()
        else:
            self.ehb.points = ehb

        # Skilling
        total_level = self.wom_data['latestSnapshot']['data']['skills']['overall']['level']

        if total_level >= 1250:
            self.level_1250.complete()
            
        if total_level >= 1500:
            self.level_1500.complete()

        if total_level >= 1750:
            self.level_1750.complete()

        if total_level >= 2000:
            self.level_2000.complete()

        if total_level >= 2100:
            self.level_2100.complete()

        if total_level >= 2200:
            self.level_2200.complete()

        if total_level >= 2277:
            self.level_2277.complete()

        ehp = int(self.wom_data['ehp'])

        if ehp >= 1250:
            self.ehp.complete()
        else:
            self.ehp.points = ehp

        # Misc
        clogs = len(self.rp_data['items'])
        self.clogs.points = clogs

        # Can't get music cape from available data I don't think

        days_in_clan = (datetime.today().replace(tzinfo=UTC) - self.join_date).days

        if days_in_clan >= 30:
            self.one_month_in_clan.complete()
            
        if days_in_clan >= 90:
            self.three_months_in_clan.complete()

        if days_in_clan >= 180:
            self.six_months_in_clan.complete()

        if days_in_clan >= 365:
            self.one_year_in_clan.complete()

        if days_in_clan >= 730:
            self.two_years_in_clan.complete()

        # Set clan points, not great but shot myself in the foot
        # with the way I set up the RankItem class. Will fix later
        self.clan_points = sum([
            getattr(self, attr).points for attr in dir(self)
            if isinstance(getattr(self, attr), RankItem)
        ])

        ranks = {
            "Helper": 0,
            "Sapphire": 500,
            "Emerald": 1000,
            "Ruby": 2000,
            "Diamond": 3500,
            "Dragonstone": 5000,
            "Onyx": 6500,
            "Zenyte": 8250,
            "Beast": 10000,
            "Wrath": 12500,
        }

        for rank, pts_required in ranks.items():
            if self.clan_points >= pts_required:
                current_rank = rank
            else:
                self.rank = current_rank
                self.next_rank = rank
                self.points_to_next_rank = pts_required - self.clan_points
                break

def parse_args():
    parser = argparse.ArgumentParser(description="HI Clan Rank Summary")
    parser.add_argument('username', type=str, help='OSRS username')
    parser.add_argument('--use-cache', action='store_true', help='Use the local /tmp cache, do not update from WoM/RuneProfile', default=True)

    return parser.parse_args()

args = parse_args()

profile = Profile(args.username, use_cache=args.use_cache)
profile.set_item_data()
profile.print_summary()
