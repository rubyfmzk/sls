import json
import urllib
import re


def hello(event, context):
  pass


def en(event, context):
  #request = {'querystring':'id=1009', 'origin':{'s3':{'customHeaders':{'x-stage':[{'value':'dev'}]}}}}
  BASE_URL = 'http://sabian-calculator.com'
  SITE_NAME = 'Sabian Calculator'

  request = event['Records'][0]['cf']['request']
  uri = request['uri']

  title = SITE_NAME
  description = 'Get your Sabian Symbols with 360 images instead of horoscope chart. Free online degree astrology website.'
  canonical_url = BASE_URL + uri

  img_num = get_img_num(request)
  og_img = get_og_img(img_num)

  if re.search('calculator', url):

    if re.search('midpoint', url):
      title = 'Midpoint Calculator | ' + SITE_NAME
      description = 'Sabian Symbols List of Midpoints'

    elif re.search('harmonics', url):
      title = 'Harmonic Renounce Calculator | ' + SITE_NAME
      description = 'List of conjunctions in harmonic charts'

    elif re.search('progression', url):
      title = 'Progression | ' + SITE_NAME
      description = 'Sabian Symbols of progression chart'

    elif re.search('solar_arc', url):
      title = 'Solar Arc | ' + SITE_NAME
      description = 'Sabian Symbols of solar arc chart'

    elif re.search('composite', url):
      title = 'Composite | ' + SITE_NAME
      description = 'Sabian Symbols List of composite chart'

    else:
      description = 'If time of birth is not accurate, this shows the range of possibilities'
      
  elif re.search('symbols/\w+/\d+', url):
    url_match = re.search(r'symbols/(\w+)/(\d+)', url)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    degree = int(url_match.group(2))
    img_num = sign['num'] * 30 + degree

    canonical_url = BASE_URL + '/' + url_match.group()
    title =  sign['en'] + ' ' + degree + ' ' + '{sabian}'  + ' | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols/\w+', url):
    url_match = re.search(r'symbols/(\w+)', url)
    sign_path = url_match.group(1)
    sign = get_sign_info(sign_path)
    img_num = sign['representative_img']

    title = sign['en'] + ' in Sabian Symbols list | ' + SITE_NAME
    og_img = get_og_img(img_num)

  elif re.search('symbols', url):
    title = 'Sabian Symbols list by zodiac signs | ' + SITE_NAME
    og_img = get_og_img(None)

  else:
    og_img = get_og_img(None)

  og_tag = '\n<title>' + title + '</title>'
  og_tag += '\n<meta name="description" content="' + description +'">'
  og_tag += '\n<meta property="og:title" content="' + title + '">'
  og_tag += '\n<meta property="og:description" content="' + description +'">'
  og_tag += '\n<meta property="og:image" content="'+og_img.url+'">'
  og_tag += '\n<meta property="og:url" content="'+canonical_url+'">'
  og_tag += '\n<meta name="twitter:card" content="'+og_img.card+'">'
  og_tag += '\n<link rel="canonical" href="'+canonical_url+'">'

  return get_response(body, og_tag)


def get_img_num(request):
  # パラメータ
  params = {k : v[0] for k, v in urllib.parse.parse_qs(request['querystring']).items()}
  if params and \
     params['img'] and \
     re.search(r'^\d{1,3}$', params['img']) and
     int(params['img']) >= 1
     int(params['img']) <= 360:
    return params['img']

  return None


def get_og_img(img_num):
  if not img_num:
    return {
      url: 'https://sabian-calculator.com/img/logo/rainbow_star_bg.png',
      card: 'summary'
    }

  img_num = int(img_num)
  img_num %= 360
  sign_num = ((img_num - 1) // 12 + 1).zfill(2)
  degree_num = ((img_num - 1) % 30 + 1).zfill(2)

  return {
    url: 'https://s3-ap-northeast-1.amazonaws.com/sabian-symbols/' + sign_num + '/' + degree_num + '.jpg',
    card: 'summary_large_image'
  }


def get_response(body, og_tag):
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
      'num': 0,
      'representative_img': '01/05.jpg',
    },
    'taurus': {
      'en': 'TAURUS',
      'ja': '牡牛座',
      'num': 1,
      'representative_img': '02/10.jpg',
    }, 
    'gemini': {
      'en': 'GEMINI',
      'ja': '双子座',
      'num': 2,
      'representative_img': '03/17.jpg',
    }, 
    'cancer': {
      'en': 'CANCER',
      'ja': '蟹座',
      'num': 3,
      'representative_img': '04/25.jpg',
    },
    'leo': {
      'en': 'LEO',
      'ja': '獅子座',
      'num': 4,
      'representative_img': '05/28.jpg',
    },
    'virgo': {
      'en': 'VIRGO',
      'ja': '乙女座',
      'num': 5,
      'representative_img': '06/04.jpg',
    },
    'libra': {
      'en': 'LIBRA',
      'ja': '天秤座',
      'num': 6,
      'representative_img': '07/03.jpg',
    },
    'scorpio': {
      'en': 'SCORPIO',
      'ja': '蠍座',
      'num': 7,
      'representative_img': '08/04.jpg',
    },
    'sagittarius': {
      'en': 'SAGITTARIUS',
      'ja': '射手座',
      'num': 8,
      'representative_img': '09/03.jpg',
    },
    'capricorn': {
      'en': 'CAPRICORN',
      'ja': '山羊座',
      'num': 9,
      'representative_img': '10/07.jpg',
    },
    'aquarius': {
      'en': 'AQUARIUS',
      'ja': '水瓶座',
      'num': 10,
      'representative_img': '11/18.jpg',
    },
    'pisces': {
      'en': 'PISCES',
      'ja': '魚座',
      'num': 11,
      'representative_img': '12/12.jpg',
    },
  }

  return SIGN_LIST[sign.lower()]



