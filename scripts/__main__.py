import sys
import webbrowser
from lab4 import Lab4
from __init__ import PATH_RESOURCES

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'script_to_run omitted'
    else:
        SCRIPT_TO_RUN = sys.argv[1]
        if SCRIPT_TO_RUN == 'lab4':
            # Instantiate Lab4 class
            SCRIPT = Lab4()
            if len(sys.argv) == 3:
                if sys.argv[2] == 'show':
                    # User want to open the webpage as well
                    webbrowser.open(PATH_RESOURCES + 'multiple_instances.html')
                    SCRIPT.run()
                elif sys.argv[2].isdigit:
                    SCRIPT.run(sys.argv[2])
            elif len(sys.argv) == 4:
                if sys.argv[2] == 'show' and sys.argv[3].isdigit:
                    webbrowser.open(PATH_RESOURCES + 'multiple_instances.html')
                    SCRIPT.run(int(sys.argv[3]))
        elif SCRIPT_TO_RUN == 'show':
            # User want to only open multiple instances
            webbrowser.open(PATH_RESOURCES + 'multiple_instances.html')
        else:
            print 'script not found!'

