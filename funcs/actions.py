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
    conn.commit()
