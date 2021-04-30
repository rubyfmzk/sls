import json
import boto3
import uuid
from urllib.parse import unquote_plus
import PIL
from PIL import Image
from io import BytesIO
from boto3.dynamodb.conditions import Key
import re


s3 = boto3.resource('s3')
bucket = 'image-manager-rubyfmzk'
ddb = boto3.resource("dynamodb")
table = ddb.Table('Collage')

def resize_put_sabian_images(event, context):

  #必要な範囲を入力
  for symbol in range(2, 3):
    for degree in range(16, 31):
      key = str(symbol).zfill(2)+'/'+str(degree).zfill(2)+'.jpg'
      _resize_put_sabian_images(key, 'sabian-symbols/full/')


def resize_put_sabian_images_by_event(event, context):
  for record in event['Records']:
    key = unquote_plus(record['s3']['object']['key'])
    _resize_put_sabian_images(key, '')

def collage(event, context):
  org_key = event['Records'][0]['s3']['object']['key']

  collage_type = 'object'
  if '/background/' in org_key:
    collage_type = 'background'
  elif '/color/' in org_key:
    collage_type = 'color'

  img_name = org_key.replace('public/collage/'+collage_type+'/', '')
  img_name = re.sub(r'\.\w+$', '', img_name)
  full_key = 'collage/'+collage_type+'/full/'+img_name+'.png'
  thumbnail_key = 'collage/'+collage_type+'/thumbnail/'+img_name+'.png'

  obj = s3.Object(
    bucket_name=bucket,
    key=org_key,
  )
  obj_body = obj.get()['Body'].read()
  img = Image.open(BytesIO(obj_body))
  img_rgba = img.convert('RGBA')
  size = img_rgba.size
  img_new = Image.new('RGBA', size)

  if collage_type == 'object':
    for x in range(size[0]):
      for y in range(size[1]):
        r,g,b,a = img_rgba.getpixel((x,y))

        alpha = int(255 - (r + g + b) / 3 * (255 / 200))

        if alpha > 255:
          alpha = 255
        elif alpha < 0:
          alpha = 0
        img_new.putpixel((x,y),(255, 255, 255, alpha))

    buffer = BytesIO()
    img_new.save(buffer, 'PNG')
    buffer.seek(0)

    obj = s3.Object(
      bucket_name=bucket,
      key=full_key,
    )
    obj.put(Body=buffer, ContentType='image/png')

  elif collage_type == 'background':
    for x in range(size[0]):
      for y in range(size[1]):
        r,g,b,a = img_rgba.getpixel((x,y))

        bright = int((r + g + b) / 3)

        if bright > 255:
          bright = 255
        elif bright < 0:
          bright = 0
        img_new.putpixel((x,y),(bright, bright, bright, 255))

    buffer = BytesIO()
    img_new.save(buffer, 'PNG')
    buffer.seek(0)

    obj = s3.Object(
      bucket_name=bucket,
      key=full_key,
    )
    obj.put(Body=buffer, ContentType='image/png')

  elif collage_type == 'color':
    source= { 'Bucket' : bucket, 'Key': org_key}
    dest = s3.Bucket(bucket)
    dest.copy(source, full_key)

  #thumbnail
  long_side = size[0] if size[0] > size[1] else size[1]
  thumbnail_x = int(size[0] / long_side * 100)
  thumbnail_y = int(size[1] / long_side * 100)
  _resize(bucket, bucket, full_key, thumbnail_key, thumbnail_x, thumbnail_y, 'PNG')


def api_collage_list(event, context):
  data = table.scan()
  return data


def api_collage_list_by_motif(event, context):
  data = table.query(
    KeyConditionExpression = Key("motif").eq(event['path']['motif'])
  )
  return data


def _resize_put_sabian_images(key, org_key_prefix):
  resize_bucket = 'sabian-symbols'
  org_key = unquote_plus(org_key_prefix + key)
  key = unquote_plus(key)

  _resize(bucket, resize_bucket, org_key, key, 480, 480)
  _resize(bucket, resize_bucket, org_key, '90px/'+key, 90, 90)
  _resize(bucket, resize_bucket, org_key, '1080px/'+key, 1080, 1080)


def _resize(org_bucket, resize_bucket, org_key, resize_key, x, y, extension='JPEG'):
  obj = s3.Object(
    bucket_name=org_bucket,
    key=org_key,
  )
  obj_body = obj.get()['Body'].read()

  img = Image.open(BytesIO(obj_body))
  img = img.resize((x, y), PIL.Image.ANTIALIAS)
  buffer = BytesIO()
  img.save(buffer, extension)
  buffer.seek(0)

  obj = s3.Object(
      bucket_name=resize_bucket,
      key=resize_key,
  )
  obj.put(Body=buffer, ContentType='image/jpeg')



