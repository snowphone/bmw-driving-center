import functools

import simplejson

loads = simplejson.loads
dumps = functools.partial(simplejson.dumps, for_json=True)
