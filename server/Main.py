import http.server
import socketserver
import json
import requests
import pandas as pd
import sqlite3
import time
import random
import os
import hashlib


class ServiceHandler(http.server.SimpleHTTPRequestHandler):
    # GET Method
    def do_GET(self):
        if self.path == "/":
            # defining all the headers
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
            regions_data = []
            hash_languages = []
            countries = []
            times = []
            data = json.loads(requests.request("GET", url, headers=headers).text)
            for information in data:
                if information["region"] and not information["region"] in regions_data:
                    regions_data.append(information["region"])

            for region in regions_data:
                start_time = time.time()
                time.sleep(3)
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

            df = pd.DataFrame({
                "Region": regions_data,
                "Country": countries,
                "Language SHA1": hash_languages,
                "Time [ms]": times
            })

            statistics = {}
            statistics['total'] = df['Time [ms]'].sum()
            statistics['mean'] = df['Time [ms]'].mean()
            statistics['min'] = df['Time [ms]'].min()
            statistics['max'] = df['Time [ms]'].max()
            df.to_json(path_or_buf='data.json')
            data_information = self.json_create()
            self.insert_data(statistics)
            self.wfile.write(json.dumps(data_information).encode())

    def json_create(self):
        script_dir = os.path.dirname(__file__)
        rel_path = "data.json"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path) as data_file:
            data_information = json.load(data_file)
        return data_information

    def insert_data(self, statistics):
        init_query = (f"""
						CREATE TABLE IF NOT EXISTS api (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						total_time REAL NOT NULL,
						mean_time REAL NOT NULL,
						min_time REAL NOT NULL,
						max_time REAL NOT NULL
						);
						INSERT INTO api (total_time, mean_time, min_time, max_time)
						VALUES ({statistics['total']}, {statistics['mean']}, {statistics['min']}, {statistics['max']});""")

        script_dir_db = os.path.dirname(__file__)  # <-- absolute dir the script
        rel_path_db = "database/api.sqlite"
        abs_file_path_db = os.path.join(script_dir_db, rel_path_db)
        try:
            connection = sqlite3.connect(abs_file_path_db)
            cursor = connection.cursor()
            print("Successfully Connected to SQLite")
            cursor.executescript(init_query)
            print("FINISHED")
            cursor.close()

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        finally:
            if (connection):
                connection.close()
                print("The SQLite connection is closed")


class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


PORT = 9000
myserver = ReuseAddrTCPServer(("", PORT), ServiceHandler)
myserver.daemon_threads = True
print(f"Server Started at http://127.0.0.1:{PORT}/")
try:
    myserver.serve_forever()
except:
    print("Closing the server.")
    myserver.server_close()
