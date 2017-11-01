#!/usr/bin/env python

class RuleManager:
	def __init__(self, rule):
		self.rule = rule
		self.globals = None
		self.locals = None

	def SetEnvironment(self, globals=None, locals=None):
		
		self.globals = globals
		self.locals = locals
		
	def Run(self):
	
		try:
			ret = eval(self.rule, self.globals, self.locals)
		except Exception, e:
			print "Error runing rule: ", e
			return None
			
		return ret
		
		
if __name__ == "__main__":

	r = "A == 3"
	rm = RuleManager( r )
	rm.SetEnvironment(locals = { 'A': 4 });
	
	ret = rm.Run()
	
	if ret != None:
		print ret
	else:
		print "error"
	
	