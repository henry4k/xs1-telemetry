import threading
import sqlite3
import datetime

class DatabaseConnection:
    def __init__( self, database, sensors ):
        self.connection = sqlite3.connect(database)
        self.sensors = sensors
        self.init_database()

    def close( self ):
        self.connection.close()
        self.conneciton = None

    def commit( self ):
        self.connection.commit()

    def init_database( self ):
        sensor_defs = [sensor+' REAL NOT NULL' for sensor in self.sensors]
        statement = '''CREATE TABLE IF NOT EXISTS measurements
                       (timestamp INTEGER NOT NULL, {})'''
        statement = statement.format(', '.join(sensor_defs))
        self.connection.execute(statement)
        self.commit()

    def insert_measurements( self, values ):
        timestamp = int(datetime.datetime.utcnow().timestamp())
        statement = '''INSERT INTO measurements (timestamp, {})
                       VALUES (?, {})'''
        statement = statement.format(', '.join(self.sensors),
                                     ', '.join(['?']*len(self.sensors)))
        self.connection.execute(statement, [timestamp]+values)

    def insert_measurement( self, sensor, value ):
        timestamp = int(datetime.datetime.utcnow().timestamp())
        statement = '''INSERT INTO measurements (timestamp, {})
                       VALUES (?, ?)'''
        statement = statement.format(sensor)
        self.connection.execute(statement, [timestamp, value])

    def read_measurements( self, sensors, startTime, endTime ):
        statement = '''SELECT timestamp, {}
                       FROM measurements
                       WHERE timestamp >= ? AND
                             timestamp <= ?
                       ORDER BY timestamp'''
        statement = statement.format(', '.join(sensors))
        cursor = self.connection.execute(statement,
                                         [int(startTime.timestamp()),
                                          int(endTime.timestamp())])
        return cursor

    def get_sensors( self ):
        return self.sensors
