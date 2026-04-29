import psycopg2
from config import load_config


def connect():
    return psycopg2.connect(**load_config())


def create_tables():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def get_player_id(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO players(username)
        VALUES(%s)
        ON CONFLICT(username) DO NOTHING;
    """, (username,))

    cur.execute("""
        SELECT id FROM players
        WHERE username = %s;
    """, (username,))

    player_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return player_id


def save_result(username, score, level):
    player_id = get_player_id(username)

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO game_sessions(player_id, score, level_reached)
        VALUES(%s, %s, %s);
    """, (player_id, score, level))

    conn.commit()
    cur.close()
    conn.close()


def get_top_scores():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.username, g.score, g.level_reached, g.played_at
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        ORDER BY g.score DESC, g.level_reached DESC
        LIMIT 10;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def get_personal_best(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(g.score)
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        WHERE p.username = %s;
    """, (username,))

    result = cur.fetchone()[0]

    cur.close()
    conn.close()

    if result is None:
        return 0
    return result