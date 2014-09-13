import signal
import threading
import json
from telemetry.xs1 import XS1Connection
from telemetry.utils import gather_sensors
from telemetry.database import DatabaseConnection
from telemetry.server import Server

class ServerThread(threading.Thread):
    def __init__( self, config ):
        threading.Thread.__init__(self)
        self.config = config
        self.server = None

    def run( self ):
        config = self.config
        database = config['database']['connection']
        graphs = config['graphs']
        sensors = gather_sensors(config)
        xs1_host = config['xs1']['host']
        server_host = config['server']['host']
        server_port = int(config['server']['port'])
        server_address = (server_host, server_port)

        xs1_connection = XS1Connection(xs1_host)
        db_connection = DatabaseConnection(database, sensors)
        server = Server(server_address,
                        xs1_connection,
                        db_connection,
                        graphs)
        self.server = server

        server.serve_forever()

        xs1_connection.close()
        db_connection.close()
        server.server_close()

if __name__ == '__main__':
    config = None
    with open('telemetry.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    server_thread = ServerThread(config)
    server_thread.start()

    signal.sigwait([signal.SIGABRT, signal.SIGINT, signal.SIGTERM])
    server_thread.server.shutdown()

    server_thread.join()
