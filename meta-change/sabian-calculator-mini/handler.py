import json
import urllib
import re
import boto3

BODY_BUCKET = 'sabian-calculator-mini-prd'

s3 = boto3.resource('s3')
#client = s3.meta.clients
client = boto3.client('s3')

def hello(event, context):
  return main(event)

def res(event, context):
  request = event['Records'][0]['cf']['request']
  uri = request['uri']

  if re.search('\.', uri):
    return request

  if re.match('/ja', uri):
    return ja(request)

  return en(request)


def en(request):
  uri = request['uri']
  og_img = get_og_img()

  BASE_URL = 'https://mini.sabian-calculator.com'
  SITE_NAME = 'Sabian Calculator Mini'

  title = SITE_NAME
  description = 'Take a look at the path of your soul\'s journey. Feel the memory of the soul, and the inner message that inspires you from the pictures and symbols.'
  canonical_url = BASE_URL + uri
  lang = 'en'

  og_tag = get_og_tag(title, description, canonical_url, og_img['url'], og_img['card'])

  return get_response(og_tag)


def ja(request):
  uri = request['uri']
  og_img = get_og_img()

  BASE_URL = 'https://mini.sabian-calculator.com/ja'
  SITE_NAME = 'サビアン計算機mini (Sabian Calculator Mini)'
  lang = 'ja'

  title = SITE_NAME
  description = 'あなたの魂の旅のみちしるべを見てみよう。絵とシンボルからひらめく魂の記憶、内なるメッセージを感じてください。'
  canonical_url = BASE_URL + uri

  og_tag = get_og_tag(title, description, canonical_url, og_img['url'], og_img['card'])

  return get_response(og_tag)


def get_og_tag(title, description, canonical_url, og_img_url, og_img_card):
  og_tag = '<title>' + title + '</title>'
  og_tag += '<meta name="description" content="' + description +'">'
  og_tag += '<meta property="og:title" content="' + title + '">'
  og_tag += '<meta property="og:description" content="' + description +'">'
  og_tag += '<meta property="og:image" content="'+og_img_url+'">'
  og_tag += '<meta property="og:url" content="'+canonical_url+'">'
  og_tag += '<meta name="twitter:card" content="'+og_img_card+'">'
  og_tag += '<link rel="canonical" href="'+canonical_url+'">'

  return og_tag


def get_og_img():
  return {
    'url': 'https://sabian-calculator.com/img/logo/rainbow_star_bg.png',
    'card': 'summary'
  }


def get_response(og_tag):
  body = client.get_object(Bucket=BODY_BUCKET, Key='index.html')
  body = body['Body'].read().decode('utf-8')
  body = re.sub(r'(<head[^>\s]*>)', "\\1" + og_tag, body)

  response = {
    'status': '200',
    'statusDescription': 'OK',
    'headers': {
      'content-type': [{
        'key': 'Content-Type',
        'value': 'text/html'
      }]
    },
    'body': body.encode('utf-8')
  }
  return response

