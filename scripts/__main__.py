import sys
from lab1 import Lab1
from resources import test_multiple_instances_path
import webbrowser

if __name__ == '__main__':

	if len(sys.argv) < 2:
		print('Arguments: script_to_run')
	else:
		script_name = sys.argv[1]
		if script_name == 'lab1':
			script = Lab1()
			if len(sys.argv) > 2 and sys.argv[2] == 'display':
				webbrowser.open(test_multiple_instances_path)
			script.run()
		else:
			print('Could not find script {}'.format(script_name))
