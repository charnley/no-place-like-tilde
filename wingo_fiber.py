
import requests
import json
import time

JERRY_URL = "https://checkout.wingo.ch/leads"


def get_address(addresstr):

    elements = addresstr.split(",")

    # assert len(elements) == 2

    left = elements[0].split()

    # assert len(left) == 2

    right = elements[1].split()

    # assert len(right) == 2

    # For example
    # address = {}
    # address['street'] = 'Luzernerring'
    # address['house_nr'] = 85
    # address['zip'] = 4056
    # address['city'] = 'Basel'

    addressdict = dict()
    addressdict['street'] = left[0].strip()
    addressdict['house_nr'] = int(left[1])
    addressdict['zip'] = int(right[0])
    addressdict['city'] = right[1].strip()

    return addressdict


def check_address(address, tech='ftth', debug=False):
    """

    """

    response, status = create_request(address, tech=tech, debug=debug)

    if status is not 200:
        return False, "Error 17"

    result, message = check_request(response['lead_id'], response['lead_token'], debug=debug)

    return result, message


def check_request(lead_id, lead_token, debug=False):
    """

    """

    lead_request = JERRY_URL + "/{lead_id}?lead_token={lead_token}"
    url = lead_request.format(lead_id=lead_id, lead_token=lead_token)

    if debug:
        print("request:", url)

    completed = False

    while not completed:

        if debug:
            print("Waiting...")

        time.sleep(5)
        r = requests.get(url)
        response = r.json()

        if "error_s" in response:
            return False, "API error"

        completed = response['completed']

    result = response['results'][0]['result']

    return result, ""


def create_request(address, tech='ftth', debug=False):
    """

    """

    payload = "check_tech={tech}&address%5Bstreet%5D={street}&address%5Bhouse_nr%5D={house_nr}&address%5Bzip%5D={zip}&address%5Bcity%5D={city}"
    payload = payload.format(**address, tech=tech)

    r = requests.post(JERRY_URL, payload)
    status = r.status_code

    if not status == 200:
        return "", status

    response = r.json()

    return response, status



def test_luzernerring():

    address = {}
    address['street'] = 'Luzernerring'
    address['house_nr'] = 85
    address['zip'] = 4056
    address['city'] = 'Basel'

    result, message = check_address(address, debug=True)
    assert result == 'success'

    return


def test_blumenrain():

    address = {}
    address['street'] = 'Blumenrain'
    address['house_nr'] = 5
    address['zip'] = 4051
    address['city'] = 'Basel'

    result, message = check_address(address, debug=True)

    assert result == "no_service"

    return


def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', type=str, help='', metavar='address in switzerland')
    args = parser.parse_args()

    # test_luzernerring()
    # test_blumenrain()

    if args.addr is None:
        print("Please specify addresse. For example 'Burgfelderstrasse 257, 4055 Basel'")
        quit()

    # address = get_address('Burgfelderstrasse 257, 4055 Basel')
    address = get_address(args.addr)

    if address:
        result, message = check_address(address)

        print(result)
        print(message)

    return

if __name__ == '__main__':
    main()

