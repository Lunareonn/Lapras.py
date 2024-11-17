import mariadb
import requests
import config
import json
from bs4 import BeautifulSoup


def setup_database(conn: mariadb.Connection):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS servers (
                 id INTEGER PRIMARY KEY AUTO_INCREMENT,
                 server_id BIGINT NOT NULL
                 );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS configs (
                 id INTEGER PRIMARY KEY AUTO_INCREMENT,
                 server_id INTEGER NOT NULL,
                 actionlogs_channel_id BIGINT,
                 autorole_id BIGINT,
                 CONSTRAINT configs_servers_FK FOREIGN KEY (server_id) REFERENCES servers(id)
                 );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS macros (
                 id INTEGER PRIMARY KEY AUTO_INCREMENT,
                 server_id INTEGER NOT NULL,
                 name TEXT NOT NULL UNIQUE,
                 alias TEXT UNIQUE,
                 content TEXT NOT NULL,
                 CONSTRAINT macros_servers_FK FOREIGN KEY (server_id) REFERENCES servers(id)
                 );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS moderation (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                server_id INTEGER NOT NULL,
                issuer_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                reason TEXT,
                count INTEGER NOT NULL,
                CONSTRAINT moderation_servers_FK FOREIGN KEY (server_id) REFERENCES servers(id)
                );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS cogs (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                server_id INTEGER NOT NULL,
                cog TEXT,
                disabled_cog BOOL,
                CONSTRAINT cog_servers_FK FOREIGN KEY (server_id) REFERENCES servers(id)
                );""")


def register_server(conn: mariadb.Connection, server_id: int):
    cur = conn.cursor()
    cur.execute("INSERT INTO servers (server_id) VALUES (?)", (server_id,))
    cur.execute("INSERT INTO configs (server_id) VALUES(?);", (cur.lastrowid,))
    conn.commit()


def set_config_autorole(conn: mariadb.Connection, server_id: int, role_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("UPDATE configs SET autorole_id = ? WHERE server_id = ?;", (role_id, fetched_server_id))
    conn.commit()


def set_config_actionlog(conn: mariadb.Connection, server_id: int, channel_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("UPDATE configs SET actionlogs_channel_id = ? WHERE server_id = ?;", (channel_id, fetched_server_id))
    conn.commit()


def fetch_actionlog_channel(conn: mariadb.Connection, server_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT actionlogs_channel_id FROM configs WHERE server_id = ?", (fetched_server_id,))
    fetched_channel_id = cur.fetchone()[0]
    return fetched_channel_id


def fetch_autorole(conn: mariadb.Connection, server_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT autorole_id FROM configs WHERE server_id = ?", (fetched_server_id,))
    fetched_role_id = cur.fetchone()[0]
    return fetched_role_id


def add_macro(conn: mariadb.Connection, server_id: int, name: str, content: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("INSERT INTO macros (server_id, name, content) VALUES (?, ?, ?)", (fetched_server_id, name, content))
    conn.commit()


def delete_macro(conn: mariadb.Connection, name: str):
    cur = conn.cursor()
    cur.execute("DELETE FROM macros WHERE name = ?", (name,))
    conn.commit()


def fetch_macro(conn: mariadb.Connection, server_id: int, name: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT content FROM macros WHERE name = ? AND server_id = ?", (name, fetched_server_id))
    content = cur.fetchone()[0]
    return content


def fetch_macro_list(conn: mariadb.Connection, server_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT name FROM macros WHERE server_id = ?", (fetched_server_id,))
    macros = cur.fetchall()
    return macros


def enable_cog(conn: mariadb.Connection, server_id: int, cog: str):
    if cog in config.loaded_cogs:
        pass
    else:
        return False

    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cog_disabled = check_if_cog_disabled(conn, server_id, cog)
    if cog_disabled is False:
        cur.execute("INSERT INTO cogs (server_id, cog, disabled_cog) VALUES (?,?,?)", (fetched_server_id, cog, False))
        conn.commit()
    else:
        cur.execute("UPDATE cogs SET disabled_cog = ? WHERE cog = ? AND server_id = ?", (False, cog, fetched_server_id))
        conn.commit()


def disable_cog(conn: mariadb.Connection, server_id: int, cog: str):
    if cog in config.loaded_cogs:
        pass
    else:
        return False

    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cog_disabled = check_if_cog_disabled(conn, server_id, cog)
    if cog_disabled is True:
        return False
    else:
        cur.execute("SELECT cog FROM cogs WHERE cog = ? AND server_id = ?", (cog, fetched_server_id))
        try:
            fetched_cog = cur.fetchone()[0]
            if cog in fetched_cog:
                cur.execute("UPDATE cogs SET disabled_cog = ? WHERE cog = ? AND server_id = ?", (True, cog, fetched_server_id))
                return conn.commit()
        except TypeError:
            cur.execute("INSERT INTO cogs (server_id, cog, disabled_cog) VALUES (?,?,?)", (fetched_server_id, cog, True))
            return conn.commit()


def check_if_cog_disabled(conn: mariadb.Connection, server_id: int, cog: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT disabled_cog FROM cogs WHERE cog = ? AND server_id = ?", (cog, fetched_server_id))
    try:
        selected_cog = cur.fetchone()[0]
        return selected_cog
    except TypeError:
        return False


def list_disabled_cogs(conn: mariadb.Connection, server_id: int):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT cog, disabled_cog FROM cogs WHERE server_id = ?", (fetched_server_id,))
    disabled_cogs = cur.fetchall()
    return disabled_cogs


def metadata_parser(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('meta', property="og:title")
    artist = soup.find('meta', attrs={'name': ['music:musician_description']})
    if artist is None:
        return

    return title["content"], artist["content"]


def fetch_lastfm(title: str, artist: str, token: str):
    genre_list = ""
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&track={title}&artist={artist}&api_key={token}&format=json"
    headers = {'content-type': 'application/json'}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)

    try:
        if json_data["message"]:
            return
    except KeyError:
        pass

    track_url = json_data["track"]["url"]
    album_url = json_data["track"]["album"]["url"]
    playcount = json_data["track"]["playcount"]
    duration = json_data["track"]["duration"]
    album_name = json_data["track"]["album"]["title"]
    cover = json_data["track"]["album"]["image"][3]["#text"]
    genres = json_data["track"]["toptags"]

    for genre in genres["tag"]:
        genre_list += f" ``{genre['name']}`` "

    return track_url, album_url, playcount, duration, album_name, cover, genre_list


def convertMillis(duration: int):
    seconds = int(duration / 1000) % 60
    minutes = int(duration / (1000 * 60)) % 60
    return minutes, seconds
