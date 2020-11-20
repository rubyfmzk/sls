import json
import boto3
import csv
import io

S3_BUCKET = 'search-city-json'
csv_key = 'csv/worldcities.csv'
json_prefix = 'v1/'

s3 = boto3.resource('s3')
s3_bucket = s3.Bucket(S3_BUCKET)

def hello(event, context):
  pass

def create_city_json(event, context):

  s3_object = s3.Object(S3_BUCKET, csv_key).get()
  city_csv = io.TextIOWrapper(io.BytesIO(s3_object['Body'].read()))

  all_cities_dict = {}

  for row in csv.DictReader(city_csv):

    #エラー
    if not (row['city'] and row['lat'] and row['lng']):
      print('error')
      print('city: ', row['city'])
      print('lat:' , row['lat'])
      print('lng: ', row['lng'])
      return 'error'

    country_key = to_key_name(row['country'])
    region_key = to_key_name(row['admin_name'])
    city_key = to_key_name(row['city'])

    if not country_key in all_cities_dict:
      all_cities_dict[country_key] = {}
      all_cities_dict[country_key]['country_name'] = to_formal_order(row['country'])
      all_cities_dict[country_key]['iso2'] = row['iso2']
      all_cities_dict[country_key]['regions'] = {}

    if region_key:
      if not region_key in all_cities_dict[country_key]['regions']:
        all_cities_dict[country_key]['regions'][region_key] = {}
        all_cities_dict[country_key]['regions'][region_key]['region_name'] = to_formal_order(row['admin_name'])
        all_cities_dict[country_key]['regions'][region_key]['cities'] = {}
      
      all_cities_dict[country_key]['regions'][region_key]['cities'][city_key] = {}
      all_cities_dict[country_key]['regions'][region_key]['cities'][city_key]['city_name'] = to_formal_order(row['city'])
      all_cities_dict[country_key]['regions'][region_key]['cities'][city_key]['lat'] = row['lat']
      all_cities_dict[country_key]['regions'][region_key]['cities'][city_key]['lon'] = row['lng']

    #香港やシンガポール
    else:
      all_cities_dict[country_key]['regions'][city_key] = {}
      all_cities_dict[country_key]['regions'][city_key]['region_name'] = to_formal_order(row['city'])
      all_cities_dict[country_key]['regions'][city_key]['cities'] = {}
      all_cities_dict[country_key]['regions'][city_key]['cities'][city_key] = {}
      all_cities_dict[country_key]['regions'][city_key]['cities'][city_key]['city_name'] = to_formal_order(row['city'])
      all_cities_dict[country_key]['regions'][city_key]['cities'][city_key]['lat'] = row['lat']
      all_cities_dict[country_key]['regions'][city_key]['cities'][city_key]['lon'] = row['lng']


  #ソート
  countries_tuple = sorted(all_cities_dict.items(), key=lambda x:x[0])
  countries_dict = {}

  for country_key, country in countries_tuple:
    countries_dict[country_key] = {}
    countries_dict[country_key]['iso2'] = all_cities_dict[country_key]['iso2']
    countries_dict[country_key]['country_name'] = all_cities_dict[country_key]['country_name']

    regions_tuple = sorted(all_cities_dict[country_key]['regions'].items(), key=lambda x:x[0])
    regions_dict = {}
    for region_key, region in regions_tuple:
      regions_dict[region_key] = {}
      regions_dict[region_key]['region_name'] = all_cities_dict[country_key]['regions'][region_key]['region_name']
      regions_dict[region_key]['cities'] = {}

      cities_tuple = sorted(all_cities_dict[country_key]['regions'][region_key]['cities'].items(), key=lambda x:x[0])
      for city_key, city in cities_tuple:
        regions_dict[region_key]['cities'][city_key] = all_cities_dict[country_key]['regions'][region_key]['cities'][city_key]

    regions_dict = json.dumps(regions_dict)
    s3_bucket.put_object(Key=json_prefix+countries_dict[country_key]['iso2']+'.json', Body=regions_dict)

  countries_dict = json.dumps(countries_dict)
  s3_bucket.put_object(Key=json_prefix+'countries.json', Body=countries_dict)


def to_key_name(area_name):
  area_name = to_ascii(area_name)
  area_name = to_formal_order(area_name)
  return area_name


# 「Korea, South」を「South Korea」に
def to_formal_order(area_name):
  area_name_array = area_name.split(', ')

  if len(area_name_array) == 2:
    return area_name_array[1] + ' ' + area_name_array[0]
  elif len(area_name_array) == 3:
    return area_name_array[2] + ' ' + area_name_array[1] + ' ' + area_name_array[0]
  return area_name


def to_ascii(text):
  accent_letter_list = {
    'À':'A', 'Á':'A', 'Â':'A', 'Ã':'A', 
    'Ä':'A', 'Å':'A', 'Æ':'AE', 'Ç':'C', 
    'È':'E', 'É':'E', 'Ê':'E', 'Ë':'E', 
    'Ì':'I', 'Í':'I', 'Î':'I', 'Ï':'I', 
    'Ð':'D', 'Ñ':'N', 'Ò':'O', 'Ó':'O', 
    'Ô':'O', 'Õ':'O', 'Ö':'O', 'Ø':'O', 
    'Ù':'U', 'Ú':'U', 'Û':'U', 'Ü':'U', 
    'Ý':'Y', 'Þ':'TH', 'ß':'s', 'à':'a', 
    'á':'a', 'â':'a', 'ã':'a', 'ä':'a', 
    'å':'a', 'æ':'ae', 'ç':'c', 'è':'e', 
    'é':'e', 'ê':'e', 'ë':'e', 'ì':'i', 
    'í':'i', 'î':'i', 'ï':'i', 'ð':'o', 
    'ñ':'n', 'ò':'o', 'ó':'o', 'ô':'o', 
    'õ':'o', 'ö':'o', 'ø':'o', 'ù':'u', 
    'ú':'u', 'û':'u', 'ü':'u', 'ý':'y', 
    'þ':'th', 'ÿ':'y', 'Ā':'A', 'ā':'a', 
    'Ă':'A', 'ă':'a', 'Ą':'A', 'ą':'a', 
    'Ć':'C', 'ć':'c', 'Ĉ':'C', 'ĉ':'c', 
    'Ċ':'C', 'ċ':'c', 'Č':'C', 'č':'c', 
    'Ď':'D', 'ď':'d', 'Đ':'D', 'đ':'d', 
    'Ē':'E', 'ē':'e', 'Ĕ':'E', 'ĕ':'e', 
    'Ė':'E', 'ė':'e', 'Ę':'E', 'ę':'e', 
    'Ě':'E', 'ě':'e', 'Ĝ':'G', 'ĝ':'g', 
    'Ğ':'G', 'ğ':'g', 'Ġ':'G', 'ġ':'g', 
    'Ģ':'G', 'ģ':'g', 'Ĥ':'H', 'ĥ':'h', 
    'Ħ':'H', 'ħ':'h', 'Ĩ':'I', 'ĩ':'i', 
    'Ī':'I', 'ī':'i', 'Ĭ':'I', 'ĭ':'i', 
    'Į':'I', 'į':'i', 'İ':'I', 'ı':'i', 
    'Ĳ':'IJ', 'ĳ':'ij', 'Ĵ':'J', 'ĵ':'j', 
    'Ķ':'K', 'ķ':'k', 'ĸ':'k', 'Ĺ':'L', 
    'ĺ':'l', 'Ļ':'L', 'ļ':'l', 'Ľ':'L', 
    'ľ':'l', 'Ŀ':'L', 'ŀ':'l', 'Ł':'L', 
    'ł':'l', 'Ń':'N', 'ń':'n', 'Ņ':'N', 
    'ņ':'n', 'Ň':'N', 'ň':'n', 'ŉ':'n', 
    'Ŋ':'NG', 'ŋ':'ng', 'Ō':'O', 'ō':'o', 
    'Ŏ':'O', 'ŏ':'o', 'Ő':'O', 'ő':'o', 
    'Œ':'OE', 'œ':'oe', 'Ŕ':'R', 'ŕ':'r', 
    'Ŗ':'R', 'ŗ':'r', 'Ř':'R', 'ř':'r', 
    'Ś':'S', 'ś':'s', 'Ŝ':'S', 'ŝ':'s', 
    'Ş':'S', 'ş':'s', 'Š':'S', 'š':'s', 
    'Ţ':'T', 'ţ':'t', 'Ť':'T', 'ť':'t', 
    'Ŧ':'T', 'ŧ':'t', 'Ũ':'U', 'ũ':'u', 
    'Ū':'U', 'ū':'u', 'Ŭ':'U', 'ŭ':'u', 
    'Ů':'U', 'ů':'u', 'Ű':'U', 'ű':'u', 
    'Ų':'U', 'ų':'u', 'Ŵ':'W', 'ŵ':'w', 
    'Ŷ':'Y', 'ŷ':'y', 'Ÿ':'Y', 'Ź':'Z', 
    'ź':'z', 'Ż':'Z', 'ż':'z', 'Ž':'Z', 
    'ž':'z', 'ſ':'S', 'ƒ':'f', 'Ơ':'O', 
    'ơ':'o', 'Ư':'U', 'ư':'u', 'Ǎ':'A', 
    'ǎ':'a', 'Ǐ':'I', 'ǐ':'i', 'Ǒ':'O', 
    'ǒ':'o', 'Ǔ':'U', 'ǔ':'u', 'Ǖ':'U', 
    'ǖ':'u', 'Ǘ':'U', 'ǘ':'u', 'Ǚ':'U', 
    'ǚ':'u', 'Ǜ':'U', 'ǜ':'u', 'Ǻ':'A', 
    'ǻ':'a', 'Ǽ':'AE', 'ǽ':'ae', 'Ǿ':'O', 
    'ǿ':'o', 'Ά':'A', '·':'', 'Έ':'E', 
    'Ή':'H', 'Ί':'I', 'Ό':'O', 'Ύ':'Y', 
    'Ώ':'O', 'ΐ':'I'
  }

  for i in accent_letter_list:
    text = text.replace(i, accent_letter_list[i])

  return text