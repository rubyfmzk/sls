import json
import boto3
import uuid
from urllib.parse import unquote_plus
import PIL
from PIL import Image

s3_client = boto3.client('s3')
resize_bucket = 'sabian-symbols'

def hello(event, context):
  _copy_all()


def resize_put_image(event, context):
  for record in event['Records']:
    bucket = record['s3']['bucket']['name']
    
    key = unquote_plus(record['s3']['object']['key'])
    tmpkey = key.replace('/', '')

    download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
    upload_path = '/tmp/resized-{}'.format(tmpkey)
    
    s3_client.download_file(bucket, key, download_path)
    resize(download_path, upload_path, 480)
    s3_client.upload_file(upload_path, resize_bucket, key)

    resize(download_path, upload_path, 90)
    s3_client.upload_file(upload_path, resize_bucket, '90px/'+key)


def resize(image_path, resized_path, size):
  with Image.open(image_path) as image:
    image.thumbnail((size, size))
    image.save(resized_path)


def _copy_all():
  org_bucket = 'sabian-symbols'
  new_bucket = ''
  for symbol in range(1, 13):
    for degree in range(1, 31):
      org_key = str(symbol).zfill(2)+'/'+str(degree).zfill(2)+'.jpg'
      new_key = org_key
      s3_client.copy_object(Bucket=new_bucket, Key=new_key, CopySource={'Bucket': org_bucket, 'Key': org_key})


def _resize_all():
  org_bucket = 'sabian-symbols'
  new_bucket = 'sabian-symbols'
  for symbol in range(1, 13):
    for degree in range(1, 31):

      org_key = str(symbol).zfill(2)+'/'+str(degree).zfill(2)+'.jpg'
      new_key = '90px/'+org_key
      tmpkey = org_key.replace('/', '')

      download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
      upload_path = '/tmp/resized-{}'.format(tmpkey)

      s3_client.download_file(org_bucket, org_key, download_path)
      resize(download_path, upload_path, 90)
      s3_client.upload_file(upload_path, new_bucket, '90px/'+org_key)

