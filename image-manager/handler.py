import json
import boto3
import uuid
from urllib.parse import unquote_plus
import PIL
from PIL import Image
from io import BytesIO
from boto3.dynamodb.conditions import Key
import re
import base64


s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket = 'image-manager-rubyfmzk'
ddb = boto3.resource("dynamodb")
collage_table = ddb.Table('Collage')

def resize_put_sabian_images(event, context):

  #必要な範囲を入力
  for symbol in range(2, 3):
    for degree in range(16, 31):
      key = str(symbol).zfill(2)+'/'+str(degree).zfill(2)+'.jpg'
      _resize_put_sabian_images(key, 'sabian-symbols/full/')


def resize_put_sabian_images_by_event(event, context):
  for record in event['Records']:
    org_key = unquote_plus(record['s3']['object']['key'])
    img_name = org_key.replace('public/sabian-symbols/', '')

    #フルサイズ保管
    source= { 'Bucket' : bucket, 'Key': org_key}
    dest = s3.Bucket(bucket)
    dest.copy(source, 'sabian-symbols/full/'+img_name)

    #リサイズ
    _resize_put_sabian_images(img_name, 'public/sabian-symbols/')

def collage(event, context):
  org_key = event['Records'][0]['s3']['object']['key']

  collage_type = 'object'
  if '/background/' in org_key:
    collage_type = 'background'
  elif '/color/' in org_key:
    collage_type = 'color'
  elif '/product/' in org_key:
    collage_type = 'product'

  img_name = org_key.replace('public/collage/'+collage_type+'/', '')
  img_name = re.sub(r'\.\w+$', '', img_name)
  full_key = 'collage/'+collage_type+'/full/'+img_name+'.png'
  thumbnail_key = 'collage/'+collage_type+'/thumbnail/'+img_name+'.png'

  obj = s3.Object(
    bucket_name=bucket,
    key=org_key,
  )
  obj_body = obj.get()['Body'].read()

  if '.base64' in org_key:
    obj_body = base64.b64decode(obj_body)
    
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

  elif collage_type == 'product':
    obj = s3.Object(
      bucket_name=bucket,
      key=full_key,
    )
    obj.put(Body=obj_body, ContentType='image/png')

  #thumbnail
  long_side = size[0] if size[0] > size[1] else size[1]
  thumbnail_x = int(size[0] / long_side * 100)
  thumbnail_y = int(size[1] / long_side * 100)
  _resize(bucket, bucket, full_key, thumbnail_key, thumbnail_x, thumbnail_y, 'PNG')

  #dynamoDB
  if collage_type == 'product':
    pass
  else:
    response = collage_table.put_item(
      Item={
        'motif': 'no_name',
        'image_id': img_name,
        'type': collage_type,
      }
    )


def collage_product_json(event, context):
  org_key = event['Records'][0]['s3']['object']['key']
  img_json = org_key.replace('public/collage_product_json/', '')
  full_key = 'collage/product/json/'+img_json
  source= { 'Bucket' : bucket, 'Key': org_key}
  dest = s3.Bucket(bucket)
  dest.copy(source, full_key)


def api_collage_list(event, context):
  data = collage_table.scan()
  return data


def api_collage_post(event, context):
  image_id = event['body']['image_id']
  motif = event['body']['motif']
  type_ = event['body']['type']
  Item = {
    'motif': motif,
    'image_id': image_id,
    'type': type_,
  }

  response = collage_table.put_item(Item=Item)
  return response


def api_collage_delete(event, context):
  image_id = event['path']['image_id']
  motif = event['path']['motif']
  type_ = event['path']['type']

  try:
    Key = {
      'image_id': image_id,
      'motif': motif,
    }
    collage_table.delete_item(Key=Key)
  except Exception as e:
    print(e)

  try:
    Key = 'collage/'+type_+'/full/'+image_id+'.png'
    s3_client.delete_object(Bucket=bucket, Key=Key)
  except Exception as e:
    print(e)

  try:
    Key = 'collage/'+type_+'/thumbnail/'+image_id+'.png'
    s3_client.delete_object(Bucket=bucket, Key=Key)
  except Exception as e:
    print(e)

  try:
    Key = 'collage/'+type_+'/json/'+image_id+'.json'
    s3_client.delete_object(Bucket=bucket, Key=Key)
  except Exception as e:
    print(e)


def api_collage_patch(event, context):
  image_id = event['path']['image_id']
  motif = event['path']['motif']
  new_image_id = event['body']['new_image_id']
  new_motif = event['body']['new_motif']
  type_ = event['body']['type']

  collage_table.put_item(Item={
    'motif': new_motif,
    'image_id': new_image_id,
    'type': type_,
  })
  collage_table.delete_item(Key={
    'motif': motif,
    'image_id': image_id,
  })


def api_collage_list_by_motif(event, context):
  data = collage_table.query(
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



