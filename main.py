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

# Secret Telegram Bot Token
from api_token import TOKEN
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class BotStatus(ndb.Model):
    muzz = ndb.BooleanProperty(indexed=False, default=False)
    annoy = ndb.IntegerProperty(indexed=False, default=0)

class UserStatus(ndb.Model):
    friendly = ndb.IntegerProperty(indexed=False, default=0)
    last_word = ndb.TextProperty(indexed=False)

# ================================

def setMuzz(chat_id, args):
    bs = BotStatus.get_or_insert(str(chat_id))
    bs.muzz = args
    bs.put()

def getMuzz(chat_id):
    bs = BotStatus.get_by_id(str(chat_id))
    if bs:
        return bs.muzz
    return False


def setAnnoy(chat_id, args):
    bs = BotStatus.get_or_insert(str(chat_id))
    bs.annoy = args
    bs.put()

def getAnnoy(chat_id):
    bs = BotStatus.get_by_id(str(chat_id))
    if bs:
        return bs.annoy
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
            fr = message['from']['first_name']
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

                elif text == '/muzzle':
                    reply('Manchas has been muzzled')
                    setMuzz(chat_id, True)

                elif text.startswith('/unmuzzle'):
                    reply('Manchas has been unmuzzled')
                    setMuzz(chat_id, False)

                elif text.startswith('/pet'):
                    reply('Thanks, {}!'.format(str(fr)))
                elif text.startswith('/botstatus'):
                    reply('*Bot Status*\nAnnoy: `{}`'.format(str(getAnnoy(chat_id))))

            # MESSAGE HANDLER

            elif 'mew' in text.lower():
                if getMuzz(chat_id):
                    reply('MMMPH MMMMMPHHM HHMMMMM!!!!!!!!')
                else:
                    tempBuffer = getAnnoy(chat_id)
                    if tempBuffer > 4:
                        reply('THAT\'S ENOUGH MEWING' + ('!' * (tempBuffer - 4)))
                    else:
                        reply('MEEEWWWWWWWW!!!!!!!!')
                    setAnnoy(chat_id, getAnnoy(chat_id) + 1)
                
            elif 'chuff' in text.lower():
                reply('chuffs')

            elif 'blep' in text.lower():
                setAnnoy(chat_id, getAnnoy(chat_id) - 1)
                reply('mlem ' + str(getAnnoy(chat_id)))

            elif 'mlem' in text.lower():
                setAnnoy(chat_id, getAnnoy(chat_id) - 1)
                reply('blep ' + str(getAnnoy(chat_id)))

            elif 'mow' in text.lower():
                setAnnoy(chat_id, 1)
                reply('*WOM!*')

            elif 'parabola' in text.lower():
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [(0, 255)[abs((j-256)**2 - (i-128)) < 30] for i in range(512) for j in range(512)]
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())

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

