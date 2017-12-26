import sys
import webbrowser
from lab1 import Lab1
from __init__ import PATH_RESOURCES

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'script_to_run omitted'
    else:
        script_to_run = sys.argv[1]
        print sys.argv
        if script_to_run == 'lab4':
            # Instantiate Lab4 class
            script = Lab1()
            if len(sys.argv) == 3:
                if sys.argv[2] == 'show':
                    # User want to open the webpage as well
                    webbrowser.open(PATH_RESOURCES + 'multiple_instances.html')
            script.run()
        else:
            print 'script not found!'


