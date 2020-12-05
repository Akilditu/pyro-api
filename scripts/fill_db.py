import requests
import argparse
import time
from getpass import getpass
from typing import Dict, Any, Optional
import csv

def get_token(api_url: str, login: str, pwd: str) -> str:

    response = requests.post(f"{api_url}/login/access-token",
                             data=f"username={login}&password={pwd}",
                             headers={"Content-Type": "application/x-www-form-urlencoded",
                                      "accept": "application/json"})
    if response.status_code != 200:
        raise ValueError(response.json()['detail'])
    return response.json()['access_token']


def api_request(method_type: str, route: str, headers=Dict[str, str], payload: Optional[Dict[str, Any]] = None):

    kwargs = {"json": payload} if isinstance(payload, dict) else {}

    response = getattr(requests, method_type)(route, headers=headers, **kwargs)
    assert response.status_code // 100 == 2, print(response.json()['detail'])
    return response.json()


def format_to_payload(data):
    payload = {}
    payload["name"] = data["Tours"]
    payload["lat"] = data["Latitude"]
    payload["lon"] = data["Longitude"]
    payload["lon"] = data["Longitude"]
    payload["country"] = "FR"
    payload["geocode"] = data["Département"]
    return payload


def main(args):

    api_url = getpass("API URL:") if args.api_url else f"http://localhost:{args.port}"

    # Log as superuser
    superuser_login = getpass('Login: ') if args.creds else "superuser"
    superuser_pwd = getpass() if args.creds else "superuser"

    start_ts = time.time()
    # Retrieve superuser token
    superuser_auth = {
        "Authorization": f"Bearer {get_token(api_url, superuser_login, superuser_pwd)}",
        "Content-Type": "application/json",
    }

    with open('scripts/resources/cameras.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")
        for row in csv_reader:
            payload = format_to_payload(row)
            try:
                site_id = api_request('post', f"{api_url}/sites/", superuser_auth, payload)['id']
                print(f"Created site {site_id}")
            except Exception as e:
                raise(e)

    print(f"SUCCESS in {time.time() - start_ts:.3}s")

    return


def parse_args():
    parser = argparse.ArgumentParser(description='Pyronear API End-to-End test',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('port', type=int, help='Port on localhost where the API is exposed')
    parser.add_argument('--api_url', dest="api_url", help="API url if not on localhost",
                        action="store_true")
    parser.add_argument('--creds', dest="creds", help="Enter different credentials than the default ones",
                        action="store_true")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
