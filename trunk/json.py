cj=True
try:
	import cjson#First check for cjson (fast)
except ImportError:
	cj=False
	import simplejson#If we don't have cjson, use slower simplejson

def encode(val):
	if cj:
		return cjson.encode(val)
	else:
		return simplejson.dumps(val)


def decode(val):
	if cj:
		return cjson.decode(val)
	else:
		return simplejson.loads(val)

__all__=['encode','decode']