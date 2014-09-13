import signal
import json
from telemetry.xs1 import XS1Connection
from telemetry.utils import gather_sensors
from telemetry.database import DatabaseConnection

if __name__ == '__main__':
    config = None
    with open('telemetry.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    database = config['database']['connection']
    sensors = gather_sensors(config)
    xs1_host = config['xs1']['host']
    update_interval = int(config['updater']['interval'])

    xs1_connection = XS1Connection(xs1_host)
    db_connection = DatabaseConnection(database, sensors)

    while True:
        sensor_names = db_connection.get_sensors()
        sensor_values = list()
        for sensor_name in sensor_names:
            sensor = xs1_connection.get_sensor_by_name(sensor_name)
            if sensor:
                sensor.update(xs1_connection)
                sensor_values.append(sensor.value)
            else:
                raise RuntimeError('Sensor "'+sensor_name+'" does not exist.')
        db_connection.insert_measurements(sensor_values)
        db_connection.commit()

        if signal.sigtimedwait([signal.SIGABRT,
                                signal.SIGINT,
                                signal.SIGTERM],
                               update_interval) != None:
            break

    xs1_connection.close()
    db_connection.close()
