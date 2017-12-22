'''
Main function
'''

import sys
from server import ByzantineServer, RequestHandler

if __name__ == '__main__':
    
    PORT_NUMBER = 80
    VESSEL_LIST = []
    VESSEL_ID = 0
    # Checking the arguments
    if len(sys.argv) != 3:  # 2 args, the script and the vessel name
        print "Arguments: VESSEL_ID number_of_vessels"
    else:
        # We need to know the vessel IP
        VESSEL_ID = int(sys.argv[1])
        # We need to write the other vessels IP, based on the knowledge of their number
        for i in range(1, int(sys.argv[2]) + 1):
            # We can add ourselves, we have a test in the propagation
            VESSEL_LIST.append("10.1.0.%d" % i)

    # We launch a server
    SERVER = ByzantineServer(('', PORT_NUMBER), RequestHandler, VESSEL_ID, VESSEL_LIST)
    print "Starting the server on port %d" % PORT_NUMBER

    try:
        SERVER.serve_forever()
    except KeyboardInterrupt:
        SERVER.server_close()
        print("Stopping Server")
