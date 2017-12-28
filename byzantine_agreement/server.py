'''
This module will contain all everything related to the server
'''
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import HTTPConnection
from urllib import urlencode
from urlparse import parse_qs
from threading import Thread
import ast
import time

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
        # Init General (All nodes are Generals)
        self.general = General()
        # Init profile to General
        self.profile = General()

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
        builder = HtmlBuilder()

        # Fetch voting results and write to output stream
        # Right now it temporarily shows only the votes the nodes themselves voted
        # TODO: Implement get_result to return voting vector of recieved votes
        # for all nodes
        # use build_vote_result in builders to assemble node arrays
        vote_vector = self.server.general.vote_vector

        votes_page = builder.build_vote_result(vote_vector)

        self.wfile.write(votes_page)

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
            if path[1] == 'vote':
                self.propagate_vote()
        else:
            raise ValueError, 'Unknown request path'

    def vote_attack(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Init byzantine agreement
        arg = 'Attack'

        # Set http header to OK
        self.set_http_headers(200)
        self.byzantine_agreement(arg)


    def vote_retreat(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Init byzantine agreement
        arg = 'Retreat'
        
        # Set http header to OK
        self.set_http_headers(200)
        self.byzantine_agreement(arg)

    def vote_byzantine(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Init byzantine agreement
        arg = 'Byzantine'
        
        # Set http header to OK
        self.set_http_headers(200)
        self.byzantine_agreement(arg)
    
    def byzantine_agreement(self, arg):
        '''
        Byzantine agreement algorithm
        '''
        if self.server.no_round == 1:
            # Handle round 1 behaviour
            if arg in ('Attack', 'Retreat'):
                self.handle_honest_vote(arg)
            
            elif arg == 'Byzantine':
                self.handle_byzantine_vote()

            else:
                # Unknown argument for byzantine agreement
                self.set_http_headers(400)
                raise ValueError, 'Unknown argument'
    
    def handle_honest_vote(self, arg):
        '''
        TODO: Fix pydoc
        '''
        # If no profile has been chosen yet set profile to honest
        if self.server.profile.my_profile == 'General':
            # Set profile to Honest
            self.server.profile = Honest()
            print 'Profile set to Honest'

        elif self.server.profile.my_profile == 'Byzantine':
            # Profile is set to Byzantine which can only vote through Byzantine button
            raise ValueError, 'Profile set to Byzantine cant vote attack or retreat'
        
        if self.server.profile.my_profile == 'Honest':
            # Assemble payload
            if arg == 'Attack':
                vote = self.server.profile.vote_attack()
            elif arg == 'Retreat':
                vote = self.server.profile.vote_retreat()
            else:
                raise ValueError, 'Unknown argument for byzantine agreement'

            vessel_id = self.server.vessel_id
            payload = models.vote_data(vessel_id, vote)
            
            # Set http header to OK
            self.set_http_headers(200)
            # Propagate the payload
            self.propagate_payload(payload, '/propagate/vote')
        
        else:
            # Unknown profile, set header and raise exception
            self.set_http_headers(400)
            raise ValueError, 'Unknown profile'

    def handle_byzantine_vote(self):
        '''
        TODO: Fix pydoc
        '''
        if self.server.profile.my_profile == 'General':
            # Set profile to Byzantine
            print 'Profile set to Byzantine and appended ip to node_ids'
            self.server.profile = Byzantine()
            Byzantine.node_ids.append("10.1.0.%s" % self.server.vessel_id)

        elif self.server.profile.my_profile == 'Honest':
            # Profile is set to Honest which can only vote through attack/retreat buttons
            raise ValueError, 'Profile set to Honest cant vote byzantine'
        
        if self.server.profile.my_profile == 'Byzantine':
            # Save vars for readability
            no_round = self.server.no_round
            no_nodes = len(self.server.vessels)
            no_loyal = no_nodes - len(Byzantine.node_ids)
            on_tie = self.server.on_tie


            # Wait until all votes has been recieved from all nodes
            while len(self.server.general.vote_vector.keys()) != (len(self.server.vessels) - len(Byzantine.node_ids)):
                # Print once every 3 seconds to prevent spam
                time.sleep(3)
                print 'Waiting for all votes to be recieved'

            # Setup model
            data = models.byzantine_vote_input(no_round, no_nodes, no_loyal, on_tie)

            # Set http header to OK
            self.set_http_headers(200)
            # Propagate payload
            byzantine_payload = self.server.profile.vote(data)
            self.propagate_byzantine(byzantine_payload, '/propagate/vote')

        else:
            # Unknown profile, set header and raise exception
            self.set_http_headers(400)
            raise ValueError, 'Unknown profile'

    def propagate_vote(self):
        '''
        Handle requests on the /propagate/vote endpoint
        TODO: Generalize func to handle all propagates
        '''
        post_data = self.parse_post_request()
        payload_data = post_data['payload'][0]
        parsed_data = ast.literal_eval(payload_data)
        print 'parsed data: ', parsed_data
        vote = parsed_data['vote']
        node_id = parsed_data['node_id']

        # Save recieved vote in vote vector
        self.server.general.add_to_vote_vector(node_id, vote)
    
    def propagate_byzantine(self, byzantine_payload, path=''):
        '''
        TODO: Temp pydoc
        '''
        if not path:
            path = '/propagate'
        print byzantine_payload
        ind = 0

        for vessel in self.server.vessels:
            if vessel not in self.server.profile.node_ids:
                #Send to all generals
                # Assemble payload
                payload = models.vote_data(self.server.vessel_id, byzantine_payload[ind]) 
                ind += 1
                # Spawn thread for contact_vessel
                thread = Thread(target=self.server.contact_vessel,
                                args=(vessel, path, payload))

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
