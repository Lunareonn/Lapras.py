import mariadb


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
                enabled_cog TEXT UNIQUE,
                disabled_cog TEXT UNIQUE,
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
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    selected_cog = check_disable_cog(conn, server_id, cog)
    if selected_cog:
        cur.execute("UPDATE cogs SET disabled_cog = NULL, enabled_cog = ? WHERE disabled_cog = ? AND server_id = ?", (cog, selected_cog, fetched_server_id))
        return conn.commit()
    else:
        cur.execute("INSERT INTO cogs (server_id, enabled_cog) VALUES (?,?)", (fetched_server_id, cog))
        conn.commit()


def disable_cog(conn: mariadb.Connection, server_id: int, cog: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    selected_cog = check_enable_cog(conn, server_id, cog)
    if selected_cog:
        cur.execute("UPDATE cogs SET enabled_cog = NULL, disabled_cog = ? WHERE enabled_cog = ? AND server_id = ?", (cog, selected_cog, fetched_server_id))
        return conn.commit()
    else:
        cur.execute("INSERT INTO cogs (server_id, disabled_cog) VALUES (?,?)", (fetched_server_id, cog))
        conn.commit()


def check_enable_cog(conn: mariadb.Connection, server_id: int, cog: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT enabled_cog FROM cogs WHERE enabled_cog = ? AND server_id = ?", (cog, fetched_server_id))
    try:
        selected_cog = cur.fetchone()[0]
        return selected_cog
    except TypeError:
        return False
    


def check_disable_cog(conn: mariadb.Connection, server_id: int, cog: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM servers WHERE server_id = ?", (server_id,))
    fetched_server_id = cur.fetchone()[0]
    cur.execute("SELECT disabled_cog FROM cogs WHERE disabled_cog = ? AND server_id = ?", (cog, fetched_server_id))
    try:
        selected_cog = cur.fetchone()[0]
        return selected_cog
    except TypeError:
        return False
