from waitress import serve  # NOQA
from rest import api  # NOQA

serve(api, host='127.0.0.1', port=5555)  # it is the same if i use serve(srv3)
