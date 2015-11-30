# parse.py 
#
# by wigguno
# parses the output of cl_script_help_2 from dotes
# looks for dump.txt in the same directory
# puts it straight into snippets.json
#
# TODO
# Add db of function examples

import json

# Class to hold a parsed function
class DotaFunction: 
	def __init__(self, name, descr, param, retrn):
		self.name 			= name
		self.description	= descr
		self.parameters		= param
		self.returns 		= retrn
		
		self.prefix 		= name
		self.function		= name
		
		self.baseClass = ''
		
		# If the name contains a colon, strip it out to get the intellisense string
		if ':' in name:
			self.baseClass 	= name.partition(':')[0]
			self.prefix 	= name.partition(':')[2]
			self.function	= self.prefix
				
	def getSnippet(self):
		paramList = ''
		for p in self.parameters:
			paramList += '${' + p + '}, '
			
		paramList = paramList[:-2]
	
		return {"prefix":self.prefix, "body":[self.function + '( ' + paramList + ' )'], "description":self.description}

# Class to hold a parsed enum
class DotaEnum:
	def __init__(self, name, descr, val):
		self.name = name
		self.descr = descr
		self.val = val
		
	def getSnippet(self):
		return {"prefix":self.name, "body":[self.name],"description":'(' + self.val + ') ' + self.descr}
		
		
dump_file = open("dump.txt", 'r')
dump_raw = dump_file.read()
dump_lines = dump_raw.split('\n')
dump_file.close()

out_file = open("snippets/snippets.json", 'w')
out_obj = {}

funcs = []
enums = []

# loop over all the lines in the dump
l = 0
while l < len( dump_lines ):

	# Grab a line
	line = dump_lines[l]
	
	# Skip if the line is empty
	if not line:
		l += 1
		continue
		
	# hold a group of lines
	lines = []
	
	# if the line starts with a comment like this, then a new function is defined
	if line[:5] == '---[[':
	
		# Get the function name out
		l2 = line[6:].partition(' ')
		name = l2[0]
			
		descr = l2[2][1:-3]
		retrn = 'void'
		param = []
		
		while 1:
			l += 1
			val = dump_lines[l][4:]
			
			if val[0:1] == 'r':
				retrn = val.partition(' ')[2]
				
			elif val[0:1] == 'p':
				param.append(val.partition(' ')[2])
				
			else:
				break
				
		funcs.append(DotaFunction(name, descr, param, retrn))
		
	# If the comment looks liek this, then it's an enum
	elif line[:8] == '--- Enum':
		enumgroup = line[9:]
		
		while 1:
			l += 1
			new_line = dump_lines[l]
			
			if not new_line or '---' in new_line:
				l -= 1
				break
				
			name = new_line.partition(' ')[0]
			val  = ''
			descr = ''
			
			if '=' in new_line:
				val = new_line.split(' ')[2]
			
			if '--' in new_line:
				descr = new_line.partition('--')[2]
			
			enums.append(DotaEnum(name, descr, val))	
	l += 1

for f in funcs:
	out_obj[f.name] = f.getSnippet()
	
for e in enums:
	out_obj[e.name] = e.getSnippet()
	
out_file.write(json.dumps(out_obj, indent=4))
out_file.close()