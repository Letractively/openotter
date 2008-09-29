import json
print request.contents.replace("${args}",json.encode(request.args))