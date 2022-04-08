import http.server, socketserver, json, time, requests, pandas, sqlite3
import random
import os
import hashlib


class ServiceHandler(http.server.SimpleHTTPRequestHandler):
    # Get method
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            # Get all countries
            url = "https://restcountries.com/v3.1/all"
            # Get by region
            url_countries_by_region = "https://restcountries.com/v3.1/region/{region}"

            headers = {
                'x-rapidapi-key': "921cfc17abmsh42834139575656fp12725cjsn8ce3ad10333d",
                'x-rapidapi-host': "restcountries-v1.p.rapidapi.com"
            }

            hash_languages = []
            countries = []
            times = []
            regions_data = []
            data = json.loads(requests.request("GET", url, headers=headers).text)
            for information in data:
                if information["region"] and not information["region"] in regions_data:
                    regions_data.append(information["region"])
            for region in regions_data:
                start_time = time.time()
                response_by_region = json.loads(
                    requests.request("GET", url_countries_by_region.format(region=region), headers=headers).text
                )
                country_option = random.randint(0, len(response_by_region) - 1)
                countries.append(response_by_region[country_option]['name']['common'])
                key_language = list(response_by_region[country_option]['languages'].keys())[0]
                hash_languages.append(hashlib.sha1(
                    response_by_region[country_option]['languages'][str(key_language)].encode()).hexdigest())
                end_time = time.time()
                times.append(round((end_time - start_time) * 1000, 2))
                print(countries)


class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


PORT = 9000
myserver = ReuseAddrTCPServer(("", PORT), ServiceHandler)
myserver.daemon_threads = True
print(f'Server started at http://127.0.0.1:{PORT}/')
try:
    myserver.serve_forever()
except:
    print("Closing the server")
    myserver.server_close()
