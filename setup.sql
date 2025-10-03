-- =========================================================
-- Utah Club Water Polo (SQLite Version)
-- =========================================================

-- Clubs
CREATE TABLE clubs (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT,
    state TEXT DEFAULT 'Utah',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Persons (players, coaches, refs)
CREATE TABLE persons (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date DATE,
    gender TEXT CHECK(gender IN ('Male','Female','Other')),
    email TEXT,
    phone TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Coach profiles
CREATE TABLE coach_profiles (
    person_id INTEGER PRIMARY KEY,
    license TEXT,
    notes TEXT,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE
);

-- Teams
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    age_group TEXT CHECK(age_group IN ('10U','12U','14U','16U','18U')) NOT NULL,
    gender TEXT CHECK(gender IN ('Boys','Girls')) NOT NULL,
    division TEXT CHECK(division IN ('Gold','Silver')) NOT NULL,
    team_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id) ON DELETE CASCADE,
    UNIQUE (club_id, age_group, gender, division)
);

-- Seasons
CREATE TABLE seasons (
    season_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    name TEXT,
    start_date DATE,
    end_date DATE
);

-- Tournaments
CREATE TABLE tournaments (
    tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (season_id) REFERENCES seasons(season_id) ON DELETE CASCADE
);

-- Matches
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER,
    tournament_id INTEGER,
    date DATETIME,
    location TEXT,
    round TEXT,
    team1_id INTEGER NOT NULL,
    team2_id INTEGER NOT NULL,
    team1_score INTEGER DEFAULT 0,
    team2_score INTEGER DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team1_id) REFERENCES teams(team_id) ON DELETE RESTRICT,
    FOREIGN KEY (team2_id) REFERENCES teams(team_id) ON DELETE RESTRICT,
    FOREIGN KEY (season_id) REFERENCES seasons(season_id) ON DELETE SET NULL,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE SET NULL,
    CHECK (team1_id <> team2_id)
);

-- Match referees
CREATE TABLE match_referees (
    match_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    role TEXT,
    PRIMARY KEY (match_id, person_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE
);

-- Player memberships
CREATE TABLE player_memberships (
    player_membership_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    jersey_number INTEGER,
    main_position TEXT CHECK(main_position IN ('Goalie','Driver','Center','Defender','Utility')),
    notes TEXT,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE
);

-- Coach assignments
CREATE TABLE coach_assignments (
    coach_assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    title TEXT,
    notes TEXT,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE
);

-- Referee assignments
CREATE TABLE referee_assignments (
    referee_assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    notes TEXT,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE
);

-- Event types
CREATE TABLE event_types (
    event_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

-- Match events
CREATE TABLE match_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    person_id INTEGER,
    event_type_id INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    game_time_seconds INTEGER NOT NULL,
    event_sequence INTEGER DEFAULT 0,
    caller_person_id INTEGER,
    extra_info TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE SET NULL,
    FOREIGN KEY (event_type_id) REFERENCES event_types(event_type_id) ON DELETE RESTRICT,
    FOREIGN KEY (caller_person_id) REFERENCES persons(person_id) ON DELETE SET NULL
);

-- Lineups
CREATE TABLE lineups (
    lineup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    in_pool BOOLEAN NOT NULL DEFAULT 1,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE,
    UNIQUE (match_id, team_id, person_id, quarter)
);

-- Player season stats
CREATE TABLE player_season_stats (
    player_season_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    team_id INTEGER,
    total_goals INTEGER DEFAULT 0,
    total_shots INTEGER DEFAULT 0,
    total_assists INTEGER DEFAULT 0,
    total_steals INTEGER DEFAULT 0,
    total_exclusions INTEGER DEFAULT 0,
    total_blocks INTEGER DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (season_id) REFERENCES seasons(season_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL,
    UNIQUE (person_id, season_id)
);

-- Indexes
CREATE INDEX idx_matches_date ON matches(date);
CREATE INDEX idx_players_lastname ON persons(last_name, first_name);

-- Seed event types
INSERT INTO event_types (code, name, description) VALUES
    ('SHOT', 'Shot', 'An attempted shot'),
    ('GOAL', 'Goal', 'A successful goal scored'),
    ('ASSIST', 'Assist', 'Player who assisted a goal'),
    ('STEAL', 'Steal', 'Defensive steal'),
    ('EXCLUSION', 'Exclusion', 'Player excluded (ejected)'),
    ('BLOCK', 'Block', 'Goalie or player blocked a shot'),
    ('PENALTY_SHOT', 'Penalty Shot', 'Penalty / penalty shot'),
    ('TURNOVER', 'Turnover', 'Possession lost'),
    ('TIMEOUT', 'Timeout', 'Team timeout called'),
    ('SUB', 'Substitution', 'Player substitution'),
    ('END_QUARTER', 'End of Quarter', 'End of a quarter');
