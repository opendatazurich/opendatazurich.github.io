import urllib3
import json


class TeamsWebhookException(Exception):
    """custom exception for failed webhook call"""
    pass


class ConnectorCard:
    def __init__(self, hookurl, http_timeout=50):
        self.http = urllib3.PoolManager()
        self.payload = {}
        self.hookurl = hookurl
        self.http_timeout = http_timeout

    def text(self, mtext):
        self.payload["text"] = mtext
        return self
    
    def title(self, text):
        self.payload["title"] = text
        return self

    def send(self):
        headers = {"Content-Type":"application/json"}
        r = self.http.request(
                'POST',
                f'{self.hookurl}',
                body=json.dumps(self.payload).encode('utf-8'),
                headers=headers, timeout=self.http_timeout)
        if r.status == 200: 
            return True
        else:
            raise TeamsWebhookException(r.reason)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    MSTEAMS_WEBHOOK = os.getenv('MSTEAMS_WEBHOOK')
    myTeamsMessage = ConnectorCard(MSTEAMS_WEBHOOK)
    myTeamsMessage.text("""Test  Bla Bla""")
    myTeamsMessage.title("""Dies ist der Titel""")
    myTeamsMessage.send()