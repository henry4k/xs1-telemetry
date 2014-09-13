import json
import datetime
import http.client

class XS1CommandError(RuntimeError):
    error_messages = {
         1:'invalid command',
         2:'cmd type missing',
         3:'number/name not found',
         4:'duplicate name',
         5:'invalid system',
         6:'invalid function',
         7:'invalid date/time',
         8:'object not found',
         9:'type not virtual',
        10:'syntax error',
        11:'error time range',
        12:'protocol version mismatch'}

    def __init__( self, error_code ):
        if error_code in self.error_messages:
            RuntimeError.__init__(self, self.error_messages[error_code])
        else:
            RuntimeError.__init__(self, 'unknown error code '+error_code)

class XS1Connection:
    def __init__( self, host ):
        self.connection = http.client.HTTPConnection(host)
        self.connection.connect()
        self.protocol_version = None
        self.config = None
        self.actuators = None
        self.sensors = None
        self.update_actuators()
        self.update_sensors()

    def close( self ):
        self.connection.close()
        self.connection = None

    def send_command( self, command, **kwargs ):
        url = '/control?callback=x&cmd='+command
        for name, value in kwargs.items():
            url += '&'+name+'='+str(value)
        self.connection.request('GET', url)
        response = self.connection.getresponse()
        if response.status != 200:
            return None
        raw_result = response.read().decode('utf-8')
        # Remove 'x(' and ')\n\r\n' that surround the json:
        raw_result = raw_result[2:-4]
        result = json.loads(raw_result)
        if 'error' in result:
            raise XS1CommandError(int(result['error']))
        return result

    def get_protocol_version( self ):
        if not self.protocol_version:
            protocol_info = self.send_command('get_protocol_info')
            self.protocol_version = protocol_info['version']
        return self.protocol_version

    def get_config( self ):
        if not self.config:
            self.config = self.send_command('get_config_info')
        return self.config

    def update_actuators( self ):
        self.actuators = []
        result = self.send_command('get_list_actuators')
        for i, actuator_info in enumerate(result['actuator']):
            actuator = XS1Actuator(i+1, actuator_info)
            self.actuators.append(actuator)

    def get_actuator_by_name( self, name ):
        for actuator in self.actuators:
            if actuator.name == name:
                return actuator
        return None

    def update_sensors( self ):
        self.sensors = []
        result = self.send_command('get_list_sensors')
        for i, sensor_info in enumerate(result['sensor']):
            sensor = XS1Sensor(i+1, sensor_info)
            self.sensors.append(sensor)

    def get_sensor_by_name( self, name ):
        for sensor in self.sensors:
            if sensor.name == name:
                return sensor
        return None

class XS1Object:
    def __init__( self, id, info ):
        self.id = id
        self.set(info)

    def set( self, info ):
        self.name = info['name']
        self.type = info['type']
        self.value = info['value']
        if info['utime'] != 0:
            self.utime = datetime.datetime.utcfromtimestamp(info['utime'])
        else:
            self.utime = None

    def update( self, connection ):
        raise NotImplementedError()

class XS1Actuator(XS1Object):
    def __init__( self, id, info ):
        XS1Object.__init__(self, id, info)

    def update( self, connection ):
        result = connection.send_command('get_state_actuator', number=self.id)
        set(result['actuator'])

class XS1Sensor(XS1Object):
    def __init__( self, id, info ):
        XS1Object.__init__(self, id, info)

    def update( self, connection ):
        result = connection.send_command('get_state_sensor', number=self.id)
        set(result['sensor'])
