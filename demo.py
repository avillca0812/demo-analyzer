from collections import defaultdict
from awpy.plot import gif, PLOT_SETTINGS
from tqdm import tqdm
import matplotlib.pyplot as plt

import os
from awpy import Demo
from awpy.plot import heatmap

# Demo: https://www.hltv.org/matches/2372746/spirit-vs-natus-vincere-blast-premier-spring-final-2024 (de_dust2, Map 2)
# dem = Demo("./asoka-mirage-close-loss.dem", verbose=False)
frames = []

def heat_map():

    demo_dirs = []
    for filename in os.listdir('./'):
        if filename.endswith('.dem'):
            demo_dirs.append(filename)
    
    

    map_corpus = defaultdict(lambda: defaultdict(list))

    team_name = ""
    
    for idx, demo_dir in enumerate(demo_dirs):
        print("Analyzing " + demo_dir + " ... " + "(" + str(idx+1) + "/" + str(len(demo_dirs)) + ")")
        splits = demo_dir.removesuffix(".dem").split("-")            

        team_name = splits[0]
        map_name = splits[1]
        game_name = "-".join(splits[2:])

        dem = Demo("./"+demo_dir, verbose=False)

        ticks = dem.ticks[["X", "Y", "Z","team_clan_name", "team_name", "round"]]
        player_locations = list(
            ticks.sample(10000).itertuples(index=False, name=None)
        )

        player_pistol_locations = list(
            ticks[(ticks['round'] == 1) | (ticks['round'] == 13)].sample(10000).itertuples(index=False, name=None)
        )
        # print(player_pistol_locations)

        ct_locs = []
        t_locs = []
        for player_loc in player_locations:
            if player_loc[3] == team_name and player_loc[4] == 'CT':
                ct_locs.append(player_loc)
            elif player_loc[3] == team_name and player_loc[4] == 'TERRORIST':
                t_locs.append(player_loc)

        ct_pistol_locs = []
        t_pistol_locs = []
        for pistol_player_loc in player_pistol_locations:
            if pistol_player_loc[3] == team_name and pistol_player_loc[4] == 'TERRORIST':
                t_pistol_locs.append(pistol_player_loc)
            elif pistol_player_loc[3] == team_name and pistol_player_loc[4] == 'CT':
                ct_pistol_locs.append(pistol_player_loc)

        map_corpus[map_name]["T"].extend(t_locs)
        map_corpus[map_name]["CT"].extend(ct_locs)

        map_corpus[map_name]["T-PISTOL"].extend(t_pistol_locs)
        map_corpus[map_name]["CT-PISTOL"].extend(ct_pistol_locs)

        dir_name = "./"+team_name+"/"+map_name+"/"
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

        fig, ax = heatmap(map_name="de_"+map_name, points=ct_locs, method="kde", size=300)
        file_name = dir_name + "-".join([team_name, map_name, game_name, "CT"]) + ".png"
        plt.savefig(file_name)
        ig, ax = heatmap(map_name="de_"+map_name, points=t_locs, method="kde", size=300)
        file_name = dir_name + "-".join([team_name, map_name, game_name, "T"])+".png"
        plt.savefig(file_name)
        plt.clf()
    
    for map, location_data in map_corpus.items():
        for side, data in location_data.items():
            fig, ax = heatmap(map_name="de_"+map, points=data, method="kde", size=300)
            dir_name = "./"+team_name+"/"+map+"/"
            file_name = dir_name +  "-".join([map, side]) + ".png"
            plt.savefig(file_name)
            plt.clf()



def make_gif():
    for tick in tqdm(dem.ticks[dem.ticks["round"] == 1].tick.values[::128]):
        frame_df = dem.ticks[dem.ticks["tick"] == tick]
        frame_df = frame_df[
            ["X", "Y", "Z", "health", "armor_value", "pitch", "yaw", "team_name", "name"]
        ]

        points = []
        point_settings = []

        for _, row in frame_df.iterrows():
            points.append((row["X"], row["Y"], row["Z"]))

            # Determine team and corresponding settings
            team = "ct" if row["team_name"] == "CT" else "t"
            settings = PLOT_SETTINGS[team].copy()

            # Add additional settings
            settings.update(
                {
                    "hp": row["health"],
                    "armor": row["armor_value"],
                    "direction": (row["pitch"], row["yaw"]),
                    "label": row["name"],
                }
            )

            point_settings.append(settings)

        frames.append({"points": points, "point_settings": point_settings})

    print("Finished processing frames. Creating gif...")
    gif("de_inferno", frames, "de_dust2.gif", duration=100)


heat_map()