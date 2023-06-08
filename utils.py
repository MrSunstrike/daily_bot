import requests

class GetInformationClient():
    def get_quote(self):
        url = 'http://api.forismatic.com/api/1.0/?method=getQuote&format=json&\
            lang=ru'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            quote = data["quoteText"]
            author = data["quoteAuthor"]
            return {
                'quote': quote,
                'author': author
            }
        else:
            return None
