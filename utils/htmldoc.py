import subprocess

def htmldoc(html, **options):
	""" 
	Calls `htmldoc` (http://www.htmldoc.org/) with the given options and returns its output.
	All `htmldoc` commandline options (see `man htmldoc`) are supported, just replace '-' with '_' and use True/False values 
	for options without arguments.
	"""
	args = ['htmldoc', '-t', 'pdf']
	options.setdefault('quiet', True)	
	for key, value in options.iteritems():
		if value is False:
			continue
		option = "--%s" % key.replace('_', '-')
		args.append(option)
		if value is not True:
			args.append(str(value))
	args.append('-')

	# FIXME: add error handling / sanitize options
	popen = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	result, stderr = popen.communicate(html)
	return result
