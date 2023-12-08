import parser.parser as parser
import handler.handler as handler
from http import server

if __name__ == "__main__":
    s = server.HTTPServer(("0.0.0.0", 8000), handler.HttpHandler)
    print("Server started on 0.0.0.0:8000")
    s.serve_forever()