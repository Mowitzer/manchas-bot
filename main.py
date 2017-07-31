import StringIO
import json
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '369806398:AAG6suzqg7yKEKJVo98zPeDJ8y6D3h5Bhc0'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class BotStatus(ndb.Model):
    value = ndb.BooleanProperty(indexed=False, default=False)

# ================================

def setEnabled(key, args):
    bs = BotStatus.get_or_insert(str(key))
    bs.value = args
    bs.put()

def getEnabled(key):
    bs = BotStatus.get_by_id(str(key))
    if bs:
        return bs.value
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(30)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class InfoHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(30)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getWebhookInfo'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        
        try:
        
            urlfetch.set_default_fetch_deadline(60)
            body = json.loads(self.request.body)
            self.response.write(json.dumps(body))

            update_id = body['update_id']
            try:
                message = body['message']
            except:
                message = body['edited_message']
            message_id = message.get('message_id')
            date = message.get('date')
            text = message.get('text')
            fr = message.get('from').get('id')
            chat = message['chat']
            chat_id = chat['id']

            def reply(msg=None, img=None):
                if msg:
                    resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                        'chat_id': str(chat_id),
                        'text': msg.encode('utf-8'),
                        'disable_web_page_preview': 'true',
                        'reply_to_message_id': str(message_id),
                        'parse_mode': 'Markdown',
                    })).read()
                elif img:
                    resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                        ('chat_id', str(chat_id)),
                        ('reply_to_message_id', str(message_id)),
                    ], [
                        ('photo', 'image.jpg', img),
                    ])
                else:
                    resp = None # resp is just a dummy variable

            if text.startswith('/'):
                if text.startswith('/start'):
                    reply('Manchas, at your service!')
                elif text.startswith('/muzzle'):
                    reply('Manchas has been muzzled')
                    setEnabled(1, True)
                elif text.startswith('/pet'):
                    reply('```uwu ^_^\n```')
                    setEnabled(2, False)
                elif text.startswith('/unmuzzle'):
                    reply('Manchas has been unmuzzled')
                    setEnabled(1, False)

            # MESSAGE HANDLER

            elif 'mew' in text.lower():
                if getEnabled(2):
                    reply('STOP MAKING ME MEW!')
                else:
                    if getEnabled(1):
                        reply('MMMPH MMMMMPHHM HHMMMMM!!!!!!!!')
                    else:
                        reply('MEEEWWWWWWWW!!!!!!!!')
                setEnabled(2, True)
                
            elif 'chuff' in text.lower():
                reply('chuffs')
                setEnabled(2, False)

            elif 'blep' in text.lower():
                reply('mlem')
                setEnabled(2, False)

            elif 'mlem' in text.lower():
                reply('blep')
                setEnabled(2, False)

            elif 'mow' in text.lower():
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+(i-128)+(j-128) for i in range(512) for j in range(512)]
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
                setEnabled(2, False)

            elif text == 'manchasgetfrom':
                reply("User ID: `{}`".format(str(fr)))

        except:
            self.response.set_status(200)
            self.response.write('')

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/info', InfoHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)

