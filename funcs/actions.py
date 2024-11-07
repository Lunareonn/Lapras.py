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
                 name TEXT NOT NULL,
                 alias TEXT,
                 content TEXT NOT NULL,
                 CONSTRAINT macros_servers_FK FOREIGN KEY (server_id) REFERENCES servers(id)
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
