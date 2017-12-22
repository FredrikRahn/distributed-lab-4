import sys
from lab4 import Lab4
from __init__ import PATH_RESOURCES
import webbrowser

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'script_to_run omitted'
    else:
        script_to_run = sys.argv[1]

        if script_to_run == 'lab4':
            # Instantiate Lab4 class
            script = Lab4()
            if sys.argv[2] and sys.argv[2] == 'show':
                # User want to open the webpage as well
                webbrowser.open(PATH_RESOURCES + 'multiple_instances.html')
            script.run()
        else:
            print 'script not found!'


