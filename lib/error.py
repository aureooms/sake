import inspect

class MainException(Exception):
	def __init__(self, what):
		Exception.__init__(self, what)

	def what(self):
		return self.args[0]

	def __repr__(self):
		return self.what()


class ModuleNameNotSpecifiedException(MainException):
	def __init__(self, main_module):
		MainException.__init__(self, 'Module name not specified, available modules are : %s' % (', '.join([o for o, _ in inspect.getmembers(main_module, inspect.ismodule)])))

class ModuleDoesNotExistException(MainException):
	def __init__(self, module_name, main_module):
		MainException.__init__(self, 'Module \'%s\' does not exist, available modules are : %s' % (module_name, ', '.join([o for o, _ in inspect.getmembers(main_module, inspect.ismodule)])))

class ActionNameNotSpecifiedException(MainException):
	def __init__(self, module, module_name):
		MainException.__init__(self, 'Action name in module \'%s\' not specified, available actions are : %s' % (module_name, ', '.join([o for o, _ in inspect.getmembers(module, inspect.isfunction)])))
	
class ActionDoesNotExistException(MainException):
	def __init__(self, action_name, module, module_name):
		MainException.__init__(self, 'Action \'%s\' in module \'%s\' does not exist, available actions are : %s' % (action_name, module_name, ', '.join([o for o, _ in inspect.getmembers(module, inspect.isfunction)])))

class TooFewArgumentsForActionException(MainException):
	def __init__(self, n, spec, action_name, module_name):
		MainException.__init__(self, 'Too few arguments for action \'%s\' in module \'%s\', signature is %s, got %d' % (action_name, module_name, inspect.formatargspec(*spec), n))

class TooManyArgumentsForActionException(MainException):
	def __init__(self, n, spec, action_name, module_name):
		MainException.__init__(self, 'Too many arguments for action \'%s\' in module \'%s\', signature is %s, got %d' % (action_name, module_name, inspect.formatargspec(*spec), n))