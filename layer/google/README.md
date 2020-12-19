# command
$ docker run --rm -v $(pwd):/var/task lambci/lambda:build-python3.8 pip install -r requirements.txt -t python/lib/python3.8/site-packages/
$ zip -r google.zip ./python > /dev/null

# 参考
Lambda Layersを作成する時はdocker-lambdaやyumdaが便利
https://qiita.com/hayao_k/items/a6fd8ecfb1f937246314

