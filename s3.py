'''
You need to have AWS credentials in ~/.aws/credentials
[default]
aws_access_key_id=KEY_ID
aws_secret_access_key=ACCESS_KEY

pip install boto3
'''

from flask import Flask, request, render_template
from livereload import Server, shell
import boto3

app = Flask(__name__)

# remember to use DEBUG mode for templates auto reload
# https://github.com/lepture/python-livereload/issues/144
app.debug = True

@app.route('/')
def index():
    return '''<form method=POST enctype=multipart/form-data action="upload">
    <input type=file name=s3file>
    <input type=submit>
    </form>'''

@app.route('/upload', methods=['POST'])
def upload():
    s3 = boto3.client(
        "s3",
        aws_access_key_id='[ACCESS_KEY]',
        aws_secret_access_key='[SECRET_KEY]'
    )

    s3.upload_fileobj(
        request.files['s3file'],
        'edb-cdn-downloads',
        'docs/' + request.files['s3file'].filename,
        ExtraArgs={
            "ACL": "public-read",
            "ContentType": request.files['s3file'].content_type
        }
    )

    return '<h3>File saved to s3</h3>'

# if __name__ == '__main__':
#     app.run(debug=True)

# Live reload server
# Prob want to set some sort of env flag to only do this on DEV
server = Server(app.wsgi_app)

# use custom host and port
server.serve(port=80, host='0.0.0.0')
