import datetime

def gather_sensors( config ):
    sensors = set()
    if 'sensors' in config['database']:
        sensors.update(config['database']['sensors'])
    else:
        graphs = config['graphs']
        for graph in graphs.values():
            graph_sensors = graph['sensors']
            sensors.update(graph_sensors)
    return sensors

def info( fmt, *args, **kwargs ):
    log_('INFO', fmt, *args, **kwargs)

def error( fmt, *args, **kwargs ):
    log_('ERROR', fmt, *args, **kwargs)

def log_( type, fmt, *args, **kwargs ):
    now = datetime.datetime.utcnow()
    timestr = now.strftime('%H:%M')
    message = fmt.format(*args, **kwargs)
    print('{} {}: {}'.format(timestr, type, message))
