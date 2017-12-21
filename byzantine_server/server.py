'''
This module will contain all everything related to the server
'''

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
        # Event queue
        self.event_log = {}
        # Time
        self.start_time = 0

    def contact_vessel(self, vessel_ip, path, action, seq_id, sender_id, key, value):
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
        post_content = urlencode(
            {'action': action, 'seq_id': seq_id, 'sender_id': sender_id, 'key': key, 'value': value})
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
            print(e)
        return success


    def propagate_value_to_vessels(self, path, action, seq_id, sender_id, key, value):
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
                self.contact_vessel(vessel, path, action,
                                    seq_id, sender_id, key, value)


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

    def get_request(self):
        '''
        Handles incoming GET requests and routes them accordingly
        '''
        print("Receiving a GET on path %s" % self.path)
        path = self.path[1::].split('/')

    def get_index(self):
        '''
        Fetches the Index page and all contents to be displayed
        @return: Entire page:html
        '''
        # We set the response status code to 200 (OK)
        self.set_http_headers(200)

        #fetch_index_header = board_frontpage_header_template
        #fetch_index_contents = self.board_helper()
        #fetch_index_footer = board_frontpage_footer_template

        self.wfile.write('Placeholder')


    # def board_helper(self):
    #     '''
    #     Helper func for fetching board contents
    #     @return: List of boardcontents
    #     '''
    #     fetch_index_entries = ""
    #     for entryId, entryValue in self.server.store.items():
    #         fetch_index_entries += entry_template % ("entries/" + str(
    #             entryId), int(entryId), str(entryValue[0]), str(entryValue[2]))
    #     boardcontents = boardcontents_template % ("Title", fetch_index_entries)
    #     return boardcontents


    # def request_board(self):
    #     '''
    #     Fetches the board and its contents
    #     '''
    #     self.set_http_headers(200)
    #     html_response = self.board_helper()
    #     self.wfile.write(html_response)


    # def request_entry(self, entryID):
    #     '''
    #     Retrieve an entry from store and inserts it into the entry_template
    #     @args: entryID:String, ID of entry to be retrieved
    #     @return: Entry:html
    #     '''
    #     # Find the specific value for the entry, if entry does not exist set value to None
    #     entryValue = self.server.store[entryId] if entryId in self.server.store else None
    #     # Return found entry if it exists, or return empty string if no such entry was found
    #     return entry_template % ("entries/" + entryId, entryId, entryValue) if entryValue != None else ""

    def post_request(self):
        '''
        Handles incoming POST requests and routes them accordingly
        '''
        
        print("Receiving a POST on %s" % self.path)
        path = self.path[1::].split('/')
