from cassandra.cluster import Cluster
import os

CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "db")
cassandra_session = None
cluster = None

def init_db():
    global cluster, cassandra_session
    print(f"[*] Conectando a Cassandra en: {CASSANDRA_HOST}...")
    cluster = Cluster([CASSANDRA_HOST])
    cassandra_session = cluster.connect('sentinel')
    print("[+] Conexión a Cassandra establecida con éxito.")

def close_db():
    if cluster:
        print("[*] Cerrando conexión a Cassandra...")
        cluster.shutdown()

def get_db():
    if cassandra_session is None:
        raise Exception("La base de datos no está inicializada")
    return cassandra_session