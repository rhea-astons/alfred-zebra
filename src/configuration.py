import ConfigParser, os

def LoadConfig():
	config = ConfigParser.ConfigParser()
	if len(config.read(os.path.expanduser('~/.alfredzebra.cfg'))) == 0:
		return None
	if not(config.has_section('API')):
		return None
	if not(config.has_option('API', 'url')):
		return None
	if not(config.has_option('API', 'token')):
		return None
	if not(config.has_section('WEB')):
		return None
	if not(config.has_option('WEB', 'url')):
		return None

	api_url = config.get('API', 'url')
	if api_url[-1:] != '/': api_url+='/'

	web_url = config.get('WEB', 'url')
	if web_url[-1:] != '/': web_url+='/'

	return {
		'api_url': api_url,
		'api_token': config.get('API', 'token'),
		'web_url': web_url
	}