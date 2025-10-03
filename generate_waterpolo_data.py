import random
from datetime import datetime, timedelta

NUM_CLUBS = 5
TEAMS_PER_CATEGORY = 3
PLAYERS_PER_TEAM = 7
REFS_PER_MATCH = 1
NUM_MATCHES = 25
SEASONS = [{"year": 2025, "name": "Spring 2025", "start": "2025-03-01", "end": "2025-06-01"}]
TOURNAMENTS = [{"name": "Utah Cup", "location": "Salt Lake City", "start": "2025-04-15", "end": "2025-04-17"}]
AGE_GROUPS = ['10U','12U','14U','16U','18U']
GENDERS = ['Boys','Girls']
DIVISIONS = ['Gold','Silver']
POSITIONS = ['Goalie','Driver','Center','Defender','Utility']
EVENTS = ['SHOT','GOAL','ASSIST','STEAL','EXCLUSION','BLOCK','PENALTY_SHOT','TURNOVER','TIMEOUT','SUB','END_QUARTER']

def random_date(start, end):
    d1 = datetime.strptime(start, "%Y-%m-%d")
    d2 = datetime.strptime(end, "%Y-%m-%d")
    delta = d2 - d1
    random_days = random.randint(0, delta.days)
    return (d1 + timedelta(days=random_days)).strftime("%Y-%m-%d")

sql = "-- Generated Utah Club Water Polo Data (SQLite)\n\n"

# --- Clubs ---
for c in range(1, NUM_CLUBS+1):
    sql += f"INSERT INTO clubs (club_id, name, city, state) VALUES ({c}, 'Club {c}', 'City {c}', 'Utah');\n"

# --- Persons ---
person_id = 1
persons = []
for _ in range(NUM_CLUBS * 50):
    first = f"F{random.randint(1,9999)}"
    last = f"L{random.randint(1,9999)}"
    dob = random_date("2005-01-01","2015-12-31")
    gender = random.choice(['Male','Female','Other'])
    persons.append(person_id)
    sql += f"INSERT INTO persons (person_id, first_name, last_name, birth_date, gender) VALUES ({person_id}, '{first}', '{last}', '{dob}', '{gender}');\n"
    person_id += 1

# --- Seasons ---
season_ids = []
for idx, s in enumerate(SEASONS):
    season_id = idx + 1
    sql += f"INSERT INTO seasons (season_id, year, name, start_date, end_date) VALUES ({season_id}, {s['year']}, '{s['name']}', '{s['start']}', '{s['end']}');\n"
    season_ids.append(season_id)

# --- Tournaments ---
tournament_ids = []
for idx, t in enumerate(TOURNAMENTS):
    tournament_id = idx + 1
    sql += f"INSERT INTO tournaments (tournament_id, season_id, name, location, start_date, end_date) VALUES ({tournament_id}, {season_ids[0]}, '{t['name']}', '{t['location']}', '{t['start']}', '{t['end']}');\n"
    tournament_ids.append(tournament_id)

# --- Teams & memberships & player season stats ---
team_id = 1
teams = []
player_season_added = set()  # to prevent duplicates in player_season_stats

for c in range(1, NUM_CLUBS+1):
    for age in AGE_GROUPS:
        for g in GENDERS:
            for div in DIVISIONS:
                if random.random() < 0.6:
                    continue
                team_name = f"{age} {g} {div} Club{c}"
                teams.append(team_id)
                sql += f"INSERT INTO teams (team_id, club_id, age_group, gender, division, team_name) VALUES ({team_id}, {c}, '{age}', '{g}', '{div}', '{team_name}');\n"

                # assign players to team
                team_players = random.sample(persons, PLAYERS_PER_TEAM)
                for person in team_players:
                    jersey = random.randint(1,99)
                    pos = random.choice(POSITIONS)
                    sql += f"INSERT INTO player_memberships (person_id, team_id, start_date, jersey_number, main_position) VALUES ({person}, {team_id}, '2025-03-01', {jersey}, '{pos}');\n"

                    # player season stats (one row per player per season)
                    if (person, season_ids[0]) not in player_season_added:
                        sql += f"INSERT INTO player_season_stats (person_id, season_id, team_id, total_goals, total_assists, total_shots, total_steals, total_blocks, total_exclusions) VALUES ({person}, {season_ids[0]}, {team_id}, {random.randint(0,10)}, {random.randint(0,10)}, {random.randint(0,15)}, {random.randint(0,5)}, {random.randint(0,3)}, {random.randint(0,2)});\n"
                        player_season_added.add((person, season_ids[0]))

                team_id += 1

# --- Matches, referees, events ---
for m in range(1, NUM_MATCHES+1):
    t1, t2 = random.sample(teams, 2)
    date = f"2025-04-{random.randint(1,28):02d} {random.randint(0,23):02d}:00:00"
    loc = f"Pool {random.randint(1,5)}"
    score1 = random.randint(0,15)
    score2 = random.randint(0,15)
    sql += f"INSERT INTO matches (match_id, season_id, tournament_id, date, location, team1_id, team2_id, team1_score, team2_score) VALUES ({m}, {season_ids[0]}, {tournament_ids[0]}, '{date}', '{loc}', {t1}, {t2}, {score1}, {score2});\n"

    # referees
    for _ in range(REFS_PER_MATCH):
        ref = random.choice(persons)
        sql += f"INSERT INTO match_referees (match_id, person_id, role) VALUES ({m}, {ref}, 'Referee');\n"

    # events
    total_events = max(score1, score2) + 5
    for q in range(1, 5):
        for _ in range(total_events):
            team = random.choice([t1, t2])
            person = random.choice(persons)
            evt = random.choice(EVENTS)
            evt_id = EVENTS.index(evt) + 1  # map to event_types IDs
            time_sec = random.randint(0,600)
            sql += f"INSERT INTO match_events (match_id, team_id, person_id, event_type_id, quarter, game_time_seconds) VALUES ({m}, {team}, {person}, {evt_id}, {q}, {time_sec});\n"

# --- Lineups ---
for tid in teams:
    for q in range(1,5):
        lineup_players = random.sample(persons, PLAYERS_PER_TEAM)
        for p in lineup_players:
            match = random.randint(1, NUM_MATCHES)
            sql += f"INSERT INTO lineups (match_id, team_id, person_id, quarter, in_pool) VALUES ({match}, {tid}, {p}, {q}, 1);\n"

# --- Write to file ---
with open("utah_waterpolo_data_sqlite.sql", "w") as f:
    f.write(sql)

print("SQLite data generator complete! ✅")
