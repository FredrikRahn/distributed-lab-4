'''
This module will contain all everything related to the server
'''
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import HTTPConnection
from urllib import urlencode
from urlparse import parse_qs
from threading import Thread

import models
from helper import extract_ep
from builders.html_builder import HtmlBuilder
from generals import Byzantine, Honest, General

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
        # our own ID (IP is 10.1.0.ID)
        self.vessel_id = vessel_id
        # The list of other vessels
        self.vessels = vessel_list
        # Init round to 1
        self.no_round = 1
        # Set on_tie value (Attack)
        self.on_tie = True
        # Instantiate general class, all nodes are generals
        self.general = General()
        # Init profile var
        self.profile = self.decide_profile(len(vessel_list))


    def decide_profile(self, numberOfNodes):
        """
        Decides on a profile by calling the choose_role function on the general class
        Return the class chosen
            :param numberOfNodes: Number of nodes in the network
        """
        if numberOfNodes > 0:
            role = self.general.choose_role(numberOfNodes)
            if role == 'Byzantine':
                return Byzantine()
            else:
                return Honest()
        else:
            raise ValueError, 'No nodes in the network'

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

    def propagate_payload_to_vessels(self, path, payload):
        '''
        Handles propagation of requests to vessels
        @args:	Path:String,	The path where the request will be sent
                        Action:String, 	The action that should be performed by the other vessels
                        Key:Number, 	Key that should be used in action
                        Value:String, 	Value corresponding to key
        @return:
        '''
        # TODO: Add retry if fail

        for vessel in self.vessels:
            if vessel != ("10.1.0.%s" % self.vessel_id):
                # A good practice would be to try again if the request failed
                # Here, we do it only once
                self.contact_vessel(vessel, path, payload)
    
    def byzantine_agreement(self):
        '''
        init byzantine agreement algorithm
        '''
        # Init vote_vectors
        for i in range(1, len(self.vessels)):
            self.profile.vote_vector['node_%d' % i] = None
        


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
        page_content = builder.build_page(self.server.profile.my_profile)
        self.wfile.write(page_content)

    def get_result(self):
        """
        docstring here
            :param self: temp
        """
        # We set the response status code to 200 (OK)
        self.set_http_headers(200)

        # Instantiate builder class
        #builder = HtmlBuilder()

        # Fetch voting results and write to output stream
        # Right now it temporarily shows only the votes the nodes themselves voted
        # TODO: Implement get_result to return voting vector of recieved votes
        # for all nodes
        # use build_vote_result in builders to assemble node arrays
        voting_results = self.server.profile.my_vote
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
        elif path[0] == 'propagate':
            self.propagate()
        else:
            raise ValueError, 'Unknown request path'

    def vote_attack(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Check so profile is Honest
        if self.server.profile.my_profile == 'Honest':
            # Set http header to OK
            self.set_http_headers(200)
            # Assemble payload
            vessel_id = self.server.vessel_id
            profile = self.server.profile
            payload = models.vote_data(vessel_id, profile.vote_attack)
            self.propagate_payload(payload)

        else:
            # Set http header to Bad request
            self.set_http_headers(400)
            raise TypeError, 'Wrong profile type (not honest)'

    def vote_retreat(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Check so profile is Honest
        if self.server.profile.my_profile == 'Honest':
            # Set http header to OK
            self.set_http_headers(200)
            # Assemble payload
            vessel_id = self.server.vessel_id
            profile = self.server.profile
            payload = models.vote_data(vessel_id, profile.vote_retreat)
            self.propagate_payload(payload)
        else:
            # Set http header to Bad request
            self.set_http_headers(400)
            raise TypeError, 'Wrong profile type (not honest)'

    def vote_byzantine(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Save vars for readability
        no_round = self.server.no_round
        no_nodes = len(self.server.vessels)
        no_loyal = no_nodes - General.nrByzantineAllowed
        on_tie = self.server.on_tie

        # Setup model
        model = models.byzantine_vote_input(no_round, no_nodes, no_loyal, on_tie)

        # Check so profile is byzantine
        if self.server.profile.my_profile == 'Byzantine':
            # Set http header to OK
            self.set_http_headers(200)
            byzantine_payload = self.server.profile.vote(model)
            self.propagate_byzantine(byzantine_payload)
        else:
            # Set http header to Bad request
            self.set_http_headers(400)
            raise TypeError, 'Wrong profile type (not byzantine)'

    def propagate(self):
        '''
        Handle requests on the /propagate endpoint
        '''
        payload = self.parse_post_request()
        print 'payload: ', payload
        
        # Save recieved votes in voting vector
        self.server.profile.vote_vector['%s' % payload['node_id']]
    
    def propagate_byzantine(self, byzantine_payload, path=''):
        '''
        TODO: Temp pydoc
        '''
        if not path:
            path = '/propagate'

        for i in range(1, len(self.server.vessels)):
            if i != self.server.vessel_id:
                # Send to everyone but itself
                vessel_ip = "10.1.0.%d" % i

                # Assemble payload
                payload = models.vote_data(self.server.vessel_id, byzantine_payload[i-1]) 

                # Spawn thread for contact_vessel
                thread = Thread(target=self.server.contact_vessel,
                                args=(vessel_ip, path, payload))

                # Kill the process if we kill the server
                thread.daemon = True
                # Start the thread
                thread.start()

    def propagate_payload(self, payload, path=''):
        '''
        TODO: Temp pydoc
        '''
        if not path:
            path = '/propagate'

        # Spawn thread for propagate_value_to_vessels
        thread = Thread(target=self.server.propagate_payload_to_vessels,
                        args=(path, payload))

        # Kill the process if we kill the server
        thread.daemon = True
        # Start the thread
        thread.start()
