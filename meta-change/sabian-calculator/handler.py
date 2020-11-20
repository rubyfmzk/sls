import json
import urllib
import re
import boto3

BODY_BUCKET = 'sabian-calculator-vue2-prd'

s3 = boto3.resource('s3')
client = s3.meta.client

with open('./lang/sabian_en.txt') as f:
  SABIAN_LIST_EN = f.read()
  SABIAN_LIST_EN = SABIAN_LIST_EN.split('\n')

with open('./lang/sabian_ja.txt') as f:
  SABIAN_LIST_JA = f.read()
  SABIAN_LIST_JA = SABIAN_LIST_JA.split('\n')

with open('./lang/sabian_fr.txt') as f:
  SABIAN_LIST_FR = f.read()
  SABIAN_LIST_FR = SABIAN_LIST_FR.split('\n')


def hello(event, context):
  return main(event)


def main(event, context):
  request = event['Records'][0]['cf']['request']
  uri = request['uri']

  if re.search('\.', uri):
    return request

  if re.match('/ja', uri):
    return ja(request)

  if re.match('/fr', uri):
    return fr(request)

  return en(request)


def en(request):
  uri = request['uri']
  img_num = get_img_num(request)
  og_img = get_og_img(img_num)

  BASE_URL = 'https://sabian-calculator.com'
  SITE_NAME = 'Sabian Calculator'

  title = SITE_NAME
  description = 'Get your Sabian Symbols with 360 images instead of horoscope chart. Free online degree astrology website.'
  canonical_url = BASE_URL + uri
  lang = 'en'


  if re.search('calculator', uri):

    if re.search('midpoint', uri):
      title = 'Midpoint Calculator | ' + SITE_NAME
      description = 'Sabian Symbols List of Midpoints'

    elif re.search('harmonics', uri):
      title = 'Harmonic Renounce Calculator | ' + SITE_NAME
      description = 'List of conjunctions in harmonic charts'

    elif re.search('progression', uri):
      title = 'Progression | ' + SITE_NAME
      description = 'Sabian Symbols of progression chart'

    elif re.search('solar_arc', uri):
      title = 'Solar Arc | ' + SITE_NAME
      description = 'Sabian Symbols of solar arc chart'

    elif re.search('composite', uri):
      title = 'Composite | ' + SITE_NAME
      description = 'Sabian Symbols List of composite chart'

      
  elif re.search('symbols/\w+/\d+', uri):
    url_match = re.search(r'symbols/(\w+)/(\d+)', uri)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    degree = int(url_match.group(2))
    img_num = sign['num'] * 30 + degree

    canonical_url = BASE_URL + '/' + url_match.group()
    title =  sign[lang] + ' ' + str(degree) + ' ' + SABIAN_LIST_EN[img_num - 1]  + ' | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols/\w+', uri):
    url_match = re.search(r'symbols/(\w+)', uri)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    img_num = sign['representative_img']

    title = sign[lang] + ' in Sabian Symbols list | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols', uri):
    title = 'Sabian Symbols list by zodiac signs | ' + SITE_NAME
    og_img = get_og_img(None)

  else:
    og_img = get_og_img(None)

  og_tag = get_og_tag(title, description, canonical_url, og_img['url'], og_img['card'])

  return get_response(og_tag)


def ja(request):
  uri = request['uri']
  img_num = get_img_num(request)
  og_img = get_og_img(img_num)

  BASE_URL = 'https://sabian-calculator.com/ja'
  SITE_NAME = 'Sabian Calculator (サビアン計算機)'
  lang = 'ja'

  title = SITE_NAME
  description = 'ホロスコープチャートの代わりにイラストでサビアンシンボルを見てみよう。無料オンライン西洋占星術研究サイト。'
  canonical_url = BASE_URL + uri

  if re.search('calculator', uri):

    if re.search('midpoint', uri):
      title = 'ハーフサム計算機 | ' + SITE_NAME
      description = 'ハーフサムのサビアンシンボル'

    elif re.search('harmonics', uri):
      title = 'ハーモニクス計算機 | ' + SITE_NAME
      description = 'ハーモニクスのコンジャンクションを一覧で表示'

    elif re.search('progression', uri):
      title = 'プログレス計算機 | ' + SITE_NAME
      description = 'プログレス(進行図)のサビアンシンボル'

    elif re.search('solar_arc', uri):
      title = 'ソーラーアーク計算機 | ' + SITE_NAME
      description = 'ソーラーアークのサビアンシンボル'

    elif re.search('composite', uri):
      title = 'コンポジット計算機 | ' + SITE_NAME
      description = 'コンポジットチャートのサビアンシンボル'
      
  elif re.search('symbols/\w+/\d+', uri):
    url_match = re.search(r'symbols/(\w+)/(\d+)', uri)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    degree = int(url_match.group(2))
    img_num = sign['num'] * 30 + degree

    canonical_url = BASE_URL + '/symbols/' + sign_path + '/' + str(degree)
    title =  sign[lang] + str(degree) + '度「' + SABIAN_LIST_JA[img_num - 1]  + '」 | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols/\w+', uri):
    url_match = re.search(r'symbols/(\w+)', uri)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    img_num = sign['representative_img']

    title = sign[lang] + 'のサビアンシンボル | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols', uri):
    title = '星座別のサビアンシンボル一覧 | ' + SITE_NAME
    og_img = get_og_img(None)

  else:
    og_img = get_og_img(None)

  og_tag = get_og_tag(title, description, canonical_url, og_img['url'], og_img['card'])

  return get_response(og_tag)


def fr(request):
  uri = request['uri']
  img_num = get_img_num(request)
  og_img = get_og_img(img_num)

  BASE_URL = 'https://sabian-calculator.com/fr'
  SITE_NAME = 'Sabian Calculator (Calculatrice Sabian)'
  lang = 'fr'

  title = SITE_NAME
  description = 'Obtenez vos Symboles Sabians avec 360 images au lieu du horoscope. Site Web gratuit d\'astrologie en ligne.'
  canonical_url = BASE_URL + uri


  if re.search('calculator', uri):

    if re.search('midpoint', uri):
      title = 'Point médian | ' + SITE_NAME
      description = 'Liste des Symboles Sabians du point médian'

    elif re.search('harmonics', uri):
      title = 'Résonance harmonique | ' + SITE_NAME
      description = 'Liste des conjonctions dans le horoscope harmoniques'

    elif re.search('progression', uri):
      title = 'Progression | ' + SITE_NAME
      description = 'Symboles Sabians de progression horoscope'

    elif re.search('solar_arc', uri):
      title = 'Arc solaire | ' + SITE_NAME
      description = 'Symboles Sabians de l\'arc solaire horoscope'

    elif re.search('composite', uri):
      title = 'Composite | ' + SITE_NAME
      description = 'Symboles Sabians Liste de la horoscope composite'

  elif re.search('symbols/\w+/\d+', uri):
    url_match = re.search(r'symbols/(\w+)/(\d+)', uri)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    degree = int(url_match.group(2))
    img_num = sign['num'] * 30 + degree

    canonical_url = BASE_URL + '/' + url_match.group()
    title =  sign[lang] + ' ' + str(degree) + ' ' + SABIAN_LIST_FR[img_num - 1]  + ' | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols/\w+', uri):
    url_match = re.search(r'symbols/(\w+)', uri)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    img_num = sign['representative_img']

    title = sign[lang] + ' dans la liste des Symboles Sabians | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols', uri):
    title = 'Liste des Symbols Sabians par signes du zodiaque | ' + SITE_NAME
    og_img = get_og_img(None)

  else:
    og_img = get_og_img(None)

  og_tag = get_og_tag(title, description, canonical_url, og_img['url'], og_img['card'])

  return get_response(og_tag)


def get_img_num(request):
  if not 'querystring' in request: return None

  # パラメータ
  params = {k : v[0] for k, v in urllib.parse.parse_qs(request['querystring']).items()}
  try:
    if(params and 
       params['img'] and
       re.search(r'^\d{1,3}$', params['img']) and
       int(params['img']) >= 1 and
       int(params['img']) <= 360):
      return params['img']
  except:
    return None

  return None


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


def get_og_img(img_num):
  if not img_num:
    return {
      'url': 'https://sabian-calculator.com/img/logo/rainbow_star_bg.png',
      'card': 'summary'
    }

  img_num = int(img_num)
  img_num %= 360
  sign_num = str((img_num - 1) // 30 + 1).zfill(2)
  degree_num = str((img_num - 1) % 30 + 1).zfill(2)

  return {
    'url': 'https://s3-ap-northeast-1.amazonaws.com/sabian-symbols/' + sign_num + '/' + degree_num + '.jpg',
    'card': 'summary_large_image'
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


def get_sign_info(sign):
  SIGN_LIST = {
    'aries': {
      'en': 'ARIES',
      'ja': '牡羊座',
      'fr': 'BÉLIER',
      'num': 0,
      'representative_img': 5,
    },
    'taurus': {
      'en': 'TAURUS',
      'ja': '牡牛座',
      'fr': 'TAUREAU',
      'num': 1,
      'representative_img': 40,
    }, 
    'gemini': {
      'en': 'GEMINI',
      'ja': '双子座',
      'fr': 'GÉMEAUX',
      'num': 2,
      'representative_img': 77,
    }, 
    'cancer': {
      'en': 'CANCER',
      'ja': '蟹座',
      'fr': 'CANCER',
      'num': 3,
      'representative_img': 115,
    },
    'leo': {
      'en': 'LEO',
      'ja': '獅子座',
      'fr': 'LION',
      'num': 4,
      'representative_img': 148,
    },
    'virgo': {
      'en': 'VIRGO',
      'ja': '乙女座',
      'fr': 'VIERGE',
      'num': 5,
      'representative_img': 154,
    },
    'libra': {
      'en': 'LIBRA',
      'ja': '天秤座',
      'fr': 'BALANCE',
      'num': 6,
      'representative_img': 183,
    },
    'scorpio': {
      'en': 'SCORPIO',
      'ja': '蠍座',
      'fr': 'SCORPION',
      'num': 7,
      'representative_img': 214,
    },
    'sagittarius': {
      'en': 'SAGITTARIUS',
      'ja': '射手座',
      'fr': 'SAGITTAIRE',
      'num': 8,
      'representative_img': 243,
    },
    'capricorn': {
      'en': 'CAPRICORN',
      'ja': '山羊座',
      'fr': 'CAPRICORNE',
      'num': 9,
      'representative_img': 277,
    },
    'aquarius': {
      'en': 'AQUARIUS',
      'ja': '水瓶座',
      'fr': 'VERSEAU',
      'num': 10,
      'representative_img': 318,
    },
    'pisces': {
      'en': 'PISCES',
      'ja': '魚座',
      'fr': 'POISSONS',
      'num': 11,
      'representative_img': 342,
    },
  }

  return SIGN_LIST[sign.lower()]


