#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
from pymongo import Connection
import pymongo
from numpy import nan, isnan
from numpy import array, mean, std

PORT_NUMBER = 9000

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
#Handler for the GET requests
    def do_GET(self):
        if self.path=="/":
            self.path="/examples/line-basic/index.htm"
        try:
            mimetype='text/html'
            sendReply = True
        
            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + self.path) 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                template_contents = f.read()
                result = template_contents.replace("<<<series_contents>>>", self.get_price_from_db())
                self.wfile.write(result)
                f.close()
            return
        
        except IOError:
        	self.send_error(404,'File Not Found: %s' % self.path)

    def get_price_from_db(self):
        connection = Connection()
        db = connection.bigdata
        price_records = db.price

        avg_prices = []
        for record in price_records.find():
            avg_prices.append(record['value']['avg_price'])
        
        avg_prices = [x for x in avg_prices if x > 1000 and x < 5000]

        mean_value = mean(avg_prices)
        std_value = std(avg_prices)

        normalized_prices = []
        for price in avg_prices:
            if abs((price - mean_value) / std_value) < 1.0 :
                normalized_prices.append(price)
        print "normalize finished"
        
        shrinked_price_points = []
        i = 0
        shrink_count = 10
        tmpArray = []
        for p in normalized_prices:
            tmpArray.append(p)
            i = i + 1
            if 0 == i % shrink_count :
                shrinked_price_points.append(mean(tmpArray))
                tmpArray = []
        print "shrink finished"

#        short_term_avg_prices = []
#        short_term_point_count = 3
#        for i in range(0, len(shrinked_price_points) - short_term_point_count):
#            short_term_avg_prices.append(mean(shrinked_price_points[i:i+short_term_point_count]))
        short_term_avg_prices = self.get_avg_values(shrinked_price_points, 3)
        long_term_avg_prices = self.get_avg_values(shrinked_price_points, 10)
#        print str_prices
#        series: [{
#                name: 'Avage Price',
#                data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
#            }, {
#                name: 'xxx',
#                data: [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
#            }]                                                                               
        series_data = """series: [{                                                
                name: 'Price',                                                         
                data: [""" + ', '.join(str(p) for p in shrinked_price_points) + """]},
                {name : 'short time average line',
                data : [""" + ', '.join(str(p) for p in short_term_avg_prices)  + """]},
                {name : 'long time average line',
                data : [""" + ', '.join(str(p) for p in long_term_avg_prices)  + """]}
]"""
        
        return series_data

    def get_avg_values(self, input_array, points_in_each_group):
        r = []
        for i in range(0, len(input_array) - points_in_each_group):
            r.append(mean(input_array[i:i+points_in_each_group]))
        return r

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER
    #Wait forever for incoming htto requests
    server.serve_forever()
except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()

