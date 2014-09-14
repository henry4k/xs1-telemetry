import io
import json
import urllib
import datetime
import threading
import http.server

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def writeJsonResult( self, response, result ):
        self.send_response(response)
        self.send_header('content-type', 'application/json')
        self.end_headers()
        out = io.TextIOWrapper(self.wfile, encoding='utf-8')
        json.dump(result, out, allow_nan=False, separators=(',', ':'))
        out.detach()

    def graph( self, query, graph_name ):
        if not graph_name in self.server.graphs:
            self.writeJsonResult(404, dict(error='No such graph.'))
            return

        graph = self.server.graphs[graph_name]
        sensors = graph['sensors']
        db = self.server.db_connection
        hours = int(query['hours'])

        sensor_data = list()
        for sensor in sensors:
            sensor_data.append(list())

        end   = datetime.datetime.utcnow()
        start = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        for row in db.read_measurements(sensors, start, end):
            timestamp = int(row[0])
            dt = datetime.datetime.fromtimestamp(timestamp)
            timestr = dt.strftime('%H:%M')

            sensor_values = row[1:]
            for i, sensor_value in enumerate(sensor_values):
                sensor_data[i].append(dict(
                    title=timestr,
                    value=sensor_value))

        datasequences = list()
        result = dict(
            graph=dict(
                title=graph_name,
                total=bool(graph['total']),
                type=graph['type'],
                refreshEveryNSeconds=120,
                datasequences=datasequences))

        for i, sensor in enumerate(sensors):
            datasequences.append(dict(
                title=sensor,
                datapoints=sensor_data[i]))

        self.writeJsonResult(200, result)

    def do_GET( self ):
        url = urllib.parse.urlparse(self.path)
        query = dict(urllib.parse.parse_qsl(url.query))

        if url.path.startswith('/graph/'):
            self.graph(query, url.path[len('/graph/'):])
        else:
            self.writeJsonResult(404, dict(error='No such resource.'))

class Server(http.server.HTTPServer):
    def __init__( self, address, db_connection, graphs ):
        http.server.HTTPServer.__init__(self, address, RequestHandler)
        self.db_connection = db_connection
        self.graphs = graphs
