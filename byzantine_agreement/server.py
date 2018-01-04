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
        # Init #byzantine nodes to 0
        self.no_byzantine = 0

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

        # TODO: DEBUGGING REMOVE
        print 'Number of round: ', self.server.no_round
        print 'Vectors received: ', self.server.general.vectors_received

        # Number of results to be received and received
        if self.server.profile.my_profile == 'Byzantine':
            no_results_to_receive = len(self.server.vessels) - 1
        else: 
            no_results_to_receive = len(self.server.vessels)
        no_results_received = len(self.server.general.result_vector)
        print '#results_received, #results_to_receive', no_results_received, no_results_to_receive

        # If we havent received all results, show vote_vector on page
        if no_results_received < no_results_to_receive:
            vote_vector = self.server.general.vote_vector
            votes_page = builder.build_votes_result(vote_vector)
            self.wfile.write(votes_page)
        elif no_results_to_receive <= no_results_received:
            # We have received all the results, now build them
            if self.server.no_round == 3:
                result_vector = self.server.general.result_vector
                print 'Result vector: ', result_vector
                result = self.server.general.result
                print 'Result: ', result
                votes_page = builder.build_result(result_vector, result)
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
            elif path[1] == 'vote_vector':
                self.propagate_vote_vector()
        else:
            raise ValueError, 'Unknown request path'

    def vote_attack(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Init byzantine agreement
        arg = 'Attack'

        self.byzantine_agreement(arg)


    def vote_retreat(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Init byzantine agreement
        arg = 'Retreat'
        
        self.byzantine_agreement(arg)

    def vote_byzantine(self):
        """
        TODO: Implement
            :param self: temp
        """
        # Init byzantine agreement
        arg = 'Byzantine'
        
        self.byzantine_agreement(arg)
    
    def change_round(self):
        # Logic for changing round
        no_votes_received = len(self.server.general.vote_vector.values())
        # Should receive votes from all but themselves if we're byzantine
        if self.server.profile.my_profile == 'Byzantine':
            no_votes_to_receieve = len(self.server.vessels) - 1
        else:
            no_votes_to_receieve = len(self.server.vessels)

        # Check if we have received all the vote_vectors
        no_vectors_received = len(self.server.general.vectors_received)
        # Should receive vectors from all but themselves
        no_vectors_to_receieve = len(self.server.vessels) - 1
        
        # Check so we have received all the votes as well as that we have voted on this node
        if self.server.profile.my_profile != 'General' and self.server.no_round == 1:
            # Properly check so we have recieved a profile
            if no_votes_received == no_votes_to_receieve and self.server.profile.my_vote != None:
                # Change round to 2
                self.server.no_round = 2
                self.byzantine_agreement()

        if no_vectors_received == no_vectors_to_receieve and self.server.no_round == 2:
            # Set round to 3, "final round"
            self.server.no_round = 3
            self.byzantine_agreement()

    def byzantine_agreement(self, arg=''):
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

        elif self.server.no_round == 2:    
            # Send vote_vector to all other nodes if honest
            if self.server.profile.my_profile == 'Honest':
                path = '/propagate/vote_vector'
                payload = [self.server.vessel_id, self.server.general.vote_vector.values()]
                self.propagate_payload(payload, path)

            elif self.server.profile.my_profile == 'Byzantine':
                # Handle_byzantine_vote will propagate byzantine vote_vectors to all other nodes
                self.handle_byzantine_vote()
            else:
                raise TypeError, 'Unknown Profile'
        elif self.server.no_round == 3:
            # Not technically a round, just that all vectors have been received and time to compute results
            self.compute_results()
        else:
            raise ValueError, 'Unknown round'
    
    def compute_results(self):
        # Check for majority of each element in all the voting vectors received
        # Amount received should be amount of vessels - 1
        no_vectors = len(self.server.vessels) - 1
        vector_length = len(self.server.general.vote_vector.values())
        
        # Init counting vars
        no_true = 0
        no_false = 0

        # Need nested loop to check all the values on same index in all the vectors
        for i in range(0, vector_length):
            for vector in range(0, no_vectors):
                if self.server.general.vectors_received[vector][i] is True:
                    no_true += 1
                elif self.server.general.vectors_received[vector][i] is False:
                    no_false += 1
            # Save majority result to result_vector
            if no_true > no_false:
                self.server.general.result_vector.append(True)
            elif no_false > no_true: 
                self.server.general.result_vector.append(False)
            else:
                # No majority, set value to on_tie
                self.server.general.result_vector.append(self.server.on_tie)

            # Reset counters for next index to compare
            no_true = 0
            no_false = 0

        # Now that result vector has been computed, count True/False values
        no_true = self.server.general.result_vector.count(True)
        no_false = self.server.general.result_vector.count(False)
        if no_true > no_false:
            self.server.general.result = True
        elif no_false > no_true:
            self.server.general.result = False
        elif no_false == no_true:
            # No majority, set value to on_tie
            self.server.general.result = self.server.on_tie
                

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

            self.server.general.add_to_vote_vector(vessel_id, vote)
            
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
            self.server.no_byzantine += 1
            Byzantine.node_ids.append("10.1.0.%s" % self.server.vessel_id)

        elif self.server.profile.my_profile == 'Honest':
            # Profile is set to Honest which can only vote through attack/retreat buttons
            raise ValueError, 'Profile set to Honest cant vote byzantine'
        
        if self.server.profile.my_profile == 'Byzantine':
            # Save vars for readability
            no_round = self.server.no_round
            no_nodes = len(self.server.vessels)
            no_loyal = no_nodes - self.server.no_byzantine
            on_tie = self.server.on_tie

            if no_round == 1:
                # Wait until all votes has been received from all nodes
                while len(self.server.general.vote_vector.keys()) != (len(self.server.vessels) - self.server.no_byzantine):
                    #TODO: Fix so this doesnt block so it can still receive new votes
                    # Print once every 3 seconds to prevent spam
                    time.sleep(3)
                    print 'Waiting for all votes to be received'

                # Setup model
                data = models.byzantine_vote_input(no_round, no_nodes, no_loyal, on_tie)

                # Set http header to OK
                self.set_http_headers(200)
                # Propagate payload
                byzantine_payload = self.server.profile.vote(data)
                self.propagate_byzantine(byzantine_payload, '/propagate/vote')
            elif no_round == 2:
                # Setup model
                data = models.byzantine_vote_input(no_round, no_nodes, no_loyal, on_tie)

                # Propagate payload
                byzantine_payload = self.server.profile.vote(data)

                #TODO: DEBUGGING PLS REMOF
                print 'Byzantine payload : ', byzantine_payload

                self.propagate_byzantine(byzantine_payload, '/propagate/vote_vector')

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

        # Save received vote in vote vector
        self.server.general.add_to_vote_vector(node_id, vote)

        # Do we need to change round ? 
        self.change_round()
            
    def propagate_vote_vector(self):
        '''
        Handle received vote_vectors
        '''
        
        post_data = self.parse_post_request()
        print 'Post_data: ', post_data
        node_id = post_data['payload'][0][0]
        vote_data = post_data['payload'][0][1]
        vote_vector = ast.literal_eval(vote_data)
        print 'vote_vector: ', vote_vector
        #print 'Sent from node: ', node_id

        index = int(node_id) - 1
        vote_vector[index] = ''

        # Save vote_vector in vectors_received
        self.server.general.vectors_received.append(vote_vector)
        print 'Vote_vectors received: ', self.server.general.vectors_received

        # Do we need to change round ? 
        self.change_round()
    
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
