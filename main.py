import requests
import datetime as dt
from twilio.rest import Client
import os
import json

admin_info = os.getenv('ADMIN_JSON_INFO')       #environment variable setting.
with open(admin_info, 'r') as file:
    file_contents = file.read()
    admin_json_info = json.loads(file_contents)


STOCK = 'AAPL'  #These inputs are for testing. If you want to automizate it, then set your own const value.
COMPANY_NAME = 'Apple Inc'
phone = admin_json_info['twilio']['my_phone_number']

def send_message(message_to_send, phone):
    account_sid = admin_json_info['twilio']['account_sid']  #you can put your twilio token.
    auth_token = admin_json_info['twilio']['auth_token']
    client = Client(account_sid, auth_token)

    message = client.messages.create(
            body=message_to_send,
            from_=admin_json_info['twilio']['phone_number'], #put any phone number you want to send you message.
            to= phone   #just put your phone number.
        )
    print(message.status)




current_date = dt.datetime.now().date()
yesterday = current_date - dt.timedelta(days=3)  #I has changed days=1 to days=3 because this stock api gets at least 3 days ago stock data.
before_yesterday = yesterday - dt.timedelta(days=1)

stock_parameter = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": admin_json_info['stock']['api_key']
}
response = requests.get(url="https://www.alphavantage.co/query", params=stock_parameter)
stock_data = response.json()["Time Series (Daily)"]
yesterday_stock_price = float(stock_data[str(yesterday)]["4. close"])
before_yesterday_stock_price = float(stock_data[str(before_yesterday)]["4. close"])
stock_price_difference = round((yesterday_stock_price - before_yesterday_stock_price) / yesterday_stock_price * 100)


if stock_price_difference <= -1 or stock_price_difference >= 1:  #you can change stock_price_difference value.

    news_parameter = {
        "q": COMPANY_NAME,
        "from": before_yesterday,
        "sortby": "popularity",
        "apiKey": admin_json_info['news']['api_key']
    }
    response = requests.get(url="https://newsapi.org/v2/everything", params=news_parameter)
    news_data = response.json()
    articles_list = news_data["articles"][:3]

    up_down_emoji = ""
    if stock_price_difference > 0:
        up_down_emoji = "↑"

    elif stock_price_difference < 0:
        up_down_emoji = "↓"

    for article in articles_list:
        message_to_send = f"""
        {STOCK}: {up_down_emoji}{abs(stock_price_difference)}%\n\nHeadline: {article["title"]}. ({STOCK})\n\nBrief: {article["description"]}\n\nurl: {article["url"]}
        """
        send_message(message_to_send, phone)






