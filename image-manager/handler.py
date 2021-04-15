import json
import boto3
import uuid
from urllib.parse import unquote_plus
import PIL
from PIL import Image
from io import BytesIO

s3 = boto3.resource('s3')

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


def _resize_put_sabian_images(key, org_key_prefix):
  bucket = 'image-manager-rubyfmzk'
  resize_bucket = 'sabian-symbols'
  org_key = unquote_plus(org_key_prefix + key)
  key = unquote_plus(key)

  _resize(bucket, resize_bucket, org_key, key, 480, 480)
  _resize(bucket, resize_bucket, org_key, '90px/'+key, 90, 90)
  _resize(bucket, resize_bucket, org_key, '1080px/'+key, 1080, 1080)


def _resize(org_bucket, resize_bucket, org_key, resize_key, x, y):

    obj = s3.Object(
        bucket_name=org_bucket,
        key=org_key,
    )
    obj_body = obj.get()['Body'].read()

    img = Image.open(BytesIO(obj_body))
    img = img.resize((x, y), PIL.Image.ANTIALIAS)
    buffer = BytesIO()
    img.save(buffer, 'JPEG')
    buffer.seek(0)

    obj = s3.Object(
        bucket_name=resize_bucket,
        key=resize_key,
    )
    obj.put(Body=buffer, ContentType='image/jpeg')



