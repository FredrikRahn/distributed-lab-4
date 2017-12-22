'''
This module will contain all everything related to the server
'''

from helper import extract_ep
from builders.html_builder import HtmlBuilder

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import HTTPConnection
from urllib import urlencode
from urlparse import parse_qs

# Static variables definitions
PORT_NUMBER = 80

class ByzantineServer(HTTPServer):
    '''
    Server class, contains all serverside functionality
    '''

    def __init__(self, server_address, handler, vessel_id, vessel_list):
        '''
        Init of Blackboard HTTP server
        @args:	server_address:String, Address to Server
                        handler:BaseHTTPRequestHandler, Server handler
                        node_id:Number, The ID of the node
                        vessel_list:[String], list of vessels
        @return:
        '''
        # We call the super init
        HTTPServer.__init__(self, server_address, handler)
        # we create the dictionary of values
        self.store = {}
        # We keep a variable of the next id to insert
        self.current_key = -1
        # our own ID (IP is 10.1.0.ID)
        self.vessel_id = vessel_id
        # The list of other vessels
        self.vessels = vessel_list
        # Init profile var
        self.profile = None
        # Init votes vector
        self.votes = []
        # Init results object
        self.results = {
            'vessel_id': 'temp_result',
            'result': None
        }

    def contact_vessel(self, vessel_ip, path, payload):
        '''
        Handles contact with specific vessel
        @args:	Vessel_ip:String, 	IP to the vessel
                        Path:String, 		The path where the request will be sent
                        Action:Any, 		Action to be performed
                        Key:Number, 		Key for store
                        Value:String, 		Value for store
        @return:Entire page:html
        '''
        # the Boolean variable we will return
        success = False
        # The variables must be encoded in the URL format, through urllib.urlencode
        post_content = urlencode({'payload': payload})
        # the HTTP header must contain the type of data we are transmitting, here URL encoded
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        # We should try to catch errors when contacting the vessel
        try:
            # We contact vessel:PORT_NUMBER since we all use the same port
            # We can set a timeout, after which the connection fails if nothing happened
            connection = HTTPConnection("%s:%d" % (
                vessel_ip, PORT_NUMBER), timeout=30)
            # We only use POST to send data (PUT and DELETE not supported)
            action_type = "POST"
            # We send the HTTP request
            connection.request(action_type, path, post_content, headers)
            # We retrieve the response
            response = connection.getresponse()
            # We want to check the status, the body should be empty
            status = response.status
            # If we receive a HTTP 200 - OK
            if status == 200:
                success = True
        # We catch every possible exceptions
        except Exception as e:
            print "Error while contacting %s" % vessel_ip
            # printing the error given by Python
            print e
        return success


    def propagate_value_to_vessels(self, path, payload):
        '''
        Handles propagation of requests to vessels
        @args:	Path:String,	The path where the request will be sent
                        Action:String, 	The action that should be performed by the other vessels
                        Key:Number, 	Key that should be used in action
                        Value:String, 	Value corresponding to key
        @return:
        '''
        #TODO: Add retry if fail

        for vessel in self.vessels:
            if vessel != ("10.1.0.%s" % self.vessel_id):
                # A good practice would be to try again if the request failed
                # Here, we do it only once
                self.contact_vessel(vessel, path, payload)


class RequestHandler(BaseHTTPRequestHandler):
    '''
    This class will handle all incoming requests
    '''
    def set_http_headers(self, status_code=200):
        '''
        Sets HTTP headers and status code of the response
        @args: Status_code, status code to put in header
        '''
        # We set the response status code (200 if OK, something else otherwise)
        self.send_response(status_code)
        # We set the content type to HTML
        self.send_header("Content-type", "text/html")
        # No more important headers, we can close them
        self.end_headers()

    def parse_post_request(self):
        '''
        Parses POST requests
        @args:
        @return: post_data:Dict returns dictionary of URL-encoded data
        '''
        post_data = ""
        # We need to parse the response, so we must know the length of the content
        length = int(self.headers['Content-Length'])
        # we can now parse the content using parse_qs
        post_data = parse_qs(self.rfile.read(length), keep_blank_values=1)
        # we return the data
        return post_data

    def do_GET(self):
        '''
        Handles incoming GET requests and routes them accordingly
        '''
        print "Receiving a GET on path %s" % self.path
        path = extract_ep(self.path)
        if path[0] == '':
            self.get_index()
        elif path[0] == 'vote' and path[1] == 'result':
            self.get_result()

    def get_index(self):
        '''
        Fetches the Index page and all contents to be displayed
        @return: Entire page:html
        '''
        # We set the response status code to 200 (OK)
        self.set_http_headers(200)

        # Instantiate builder class
        builder = HtmlBuilder()

        # Fetch page content and write to output stream
        page_content = builder.build_page()
        self.wfile.write(page_content)

    def get_result(self):
        # We set the response status code to 200 (OK)
        self.set_http_headers(200)

        # Instantiate builder class
        builder = HtmlBuilder()
        
        # Fetch voting results and write to output stream
        voting_results = builder.build_vote_result(self.server.votes)
        self.wfile.write(voting_results)

    def do_POST(self):
        '''
        Handles incoming POST requests and routes them accordingly
        '''
        print "Receiving a POST on %s" % self.path

        path = extract_ep(self.path)
        if path[0] == 'vote':
            if path[1] == 'attack':
                self.vote_attack()
            elif path[1] == 'retreat':
                self.vote_retreat()
            elif path[1] == 'byzantine':
                self.vote_byzantine()
    
    def vote_attack(self):
        pass

    def vote_retreat(self):
        pass

    def vote_byzantine(self):
        pass

