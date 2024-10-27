#two IFTTT applets: one for emergyency notif when bitcoin falls under threshold, and another for regular Telegram updates

import requests
import time
from datetime import datetime

BITCOIN_PRICE_THRESHOLD = 10000

BITCOIN_API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/bitcoin_price_update/with/key/A6ofmO6BBmstGuJkb34bw84KiLAwbeT3N-90P2R0Yz'

def get_latest_bitcoin_price():
    try:
        response = requests.get(BITCOIN_API_URL)
        response.raise_for_status()  # Raise an error for bad responses
        response_json = response.json()

        # Accessing the price correctly from the returned structure
        return float(response_json['bitcoin']['usd'])
    
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching Bitcoin price: {e}")
        return None

def post_ifttt_webhook(event, value, webhook_url):
    data = {'value1': value}  # The payload that will be sent to IFTTT service
    ifttt_event_url = webhook_url.format(event)  # Inserts our desired event
    response = requests.post(ifttt_event_url, json=data)  # Sends a HTTP POST request to the webhook URL

    if response.status_code == 200:
        print(f'Successfully triggered {event} with {value}')
    else:
        print(f'Failed to trigger {event}. Status code: {response.status_code}. Response: {response.text}')

def format_bitcoin_history(bitcoin_history):
    rows = []
    for bitcoin_price in bitcoin_history:
        date = bitcoin_price['date'].strftime('%d.%m.%Y %H:%M')
        price = bitcoin_price['price']
        row = '{}: $<b>{}</b>'.format(date, price)
        rows.append(row)

    return '<br>'.join(rows)


def main():
    bitcoin_history = []
    while True:
        price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_history.append({'date': date, 'price': price})

        if price < BITCOIN_PRICE_THRESHOLD:
            post_ifttt_webhook('bitcoin_price_emergency', price, 'https://maker.ifttt.com/trigger/bitcoin_price_emergency/with/key/A6ofmO6BBmstGuJkb34bw84KiLAwbeT3N-90P2R0Yz')

        if len(bitcoin_history) == 5:
            post_ifttt_webhook('bitcoin_price_update', format_bitcoin_history(bitcoin_history), IFTTT_WEBHOOKS_URL)
            # Reset the history
            bitcoin_history = []
        
        time.sleep(5*60)

if __name__ == '__main__':
    main()

    