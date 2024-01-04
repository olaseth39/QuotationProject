import requests


# api_key = "YONMNJKB756OENKK"

# from_c = "NGN"
# to_c = "USD"
base_url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"
# main_url = base_url + '&from_currency=' + from_c + '&to_currency=' + to_c + '&apikey=' + api_key


class CurrencyConverter():
    def __init__(self, api):
        self.api = api

    def convert_to_usd(self,from_c, to_usd):
        main_url = base_url + '&from_currency=' + from_c + '&to_currency=' + to_usd + '&apikey=' + self.api
        response = requests.get(main_url)
        exchange_values = response.json()

        # get the dollar conversion
        usd_er = float(exchange_values['Realtime Currency Exchange Rate']['5. Exchange Rate'])

        return usd_er

    def convert_to_currency(self, to_c):
        main_url = base_url + '&from_currency=' + "USD" + '&to_currency=' + to_c + '&apikey=' + self.api
        response = requests.get(main_url)
        exchange_values = response.json()

        # get the dollar conversion
        usd_to_currency_code = float(exchange_values['Realtime Currency Exchange Rate']['5. Exchange Rate'])

        return usd_to_currency_code


