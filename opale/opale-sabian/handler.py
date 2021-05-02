import json
import boto3
import uuid
from urllib.parse import unquote_plus
import PIL
from PIL import Image
import numpy as np

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket = 'opale-sabian'
tmp_npy = '/tmp/a.npy'
tmp_jpg = '/tmp/a.jpg'

def hello(event, context):
  #resize_and_save_all(15)
  save_luminance_vector(15)


def save_luminance_vector(px):
  dir = str(px) + 'px'
  arr_row = px ** 2

  vec = get_luminance_vector(dir, arr_row)
  
  #npのバイナリを保存
  np.save(tmp_npy, vec)
  s3_client.upload_file(tmp_npy, bucket, 'data/'+dir+'/luminance_org.npy')

  #jsonを保存
  vec_json = vec.tolist()
  obj = s3.Object(bucket, 'data/'+dir+'/luminance_org.json')
  obj.put(Body = json.dumps(vec_json))


def get_luminance_vector(dir, arr_row):
  vec = np.empty((0, arr_row), dtype=int)

  for symbol in range(1, 361):
    key = dir+'/'+str(symbol).zfill(3)+'.jpg'
    img_arr = get_luminance_array_from_key(key)
    vec = np.append(vec, np.array([img_arr]), axis=0)

  return vec


def save_luminance_image_from_key(key, dir):
  download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
  s3_client.download_file(bucket, key, download_path)
  with Image.open(download_path) as image:
    #輝度のグレースケールに変換
    image = image.convert('L')
    #一次元配列
    image = np.ravel(image)
    return image



def get_luminance_array_from_key(key):
  tmpkey = key.replace('/', '')
  download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
  s3_client.download_file(bucket, key, download_path)
  with Image.open(download_path) as image:
    #輝度のグレースケールに変換
    image = image.convert('L')
    #一次元配列
    image = np.ravel(image)
    return image


def resize(image_path, resized_path, size):
  with Image.open(image_path) as image:
    image.thumbnail((size, size))
    image.save(resized_path)


def resize_and_save_all(px):
  for symbol in range(1, 361):
      org_key = 'base_image/'+str(symbol).zfill(3)+'.jpg'
      new_key = str(px)+'px/'+str(symbol).zfill(3)+'.jpg'
      tmpkey = org_key.replace('/', '')

      download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
      upload_path = '/tmp/resized-{}'.format(tmpkey)

      s3_client.download_file(bucket, org_key, download_path)
      resize(download_path, upload_path, px)
      s3_client.upload_file(upload_path, bucket, new_key)


