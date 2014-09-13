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
