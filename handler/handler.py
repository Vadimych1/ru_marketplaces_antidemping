from http import server

INTERFACE_PATH = "./interface/"

class HttpHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        path = self.path
        print(path)

        try:
            with open(INTERFACE_PATH+("index.html" if path == "/" else path if path.endswith(".html") else path+".html"), "r", -1, "utf-8") as f:
                self.wfile.write(f.read().encode("utf-8"))
        except:
            with open(INTERFACE_PATH+"404notfound.html", "r", -1, "utf-8") as f:
                self.wfile.write(f.read().encode("utf-8"))