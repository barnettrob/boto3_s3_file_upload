from flask import Flask, flash, request, render_template, redirect
import boto3
import os

ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', path=request.script_root)

@app.route('/upload', methods=['POST'])
def upload():
    index_page = request.url_root

    if 's3file' not in request.files:
        flash('Something went wrong. No file found')
        return redirect(request.url)

    if request.files['s3file'].filename == '':
        flash('No file selected')

    if request.files['s3file'] and allowed_file(request.files['s3file'].filename):
        # Store access key and secret key for s3 bucket uploading to in a config file
        # uploaded to your other s3 bucket. Point to this config file in zappa_settings.json:
        # {
        #     "dev": {
        #         ...
        #     "remote_env": "s3://my-other-bucket/super-secret-config.json",
        # },
        # ...
        # }
        access_key = os.environ.get('access_key')
        secret_key = os.environ.get('secret_key')

        s3 = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
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

        file_url = 'https://get.enterprisedb.com/docs/' + request.files['s3file'].filename
        return '''<h3>File saved to s3 bucket</h3>
                <p><a href="''' + file_url + '" target="_blank">' + file_url + '''</a></p>
                <p><a href="''' + index_page + '">Upload another file</a></p>'
    else:
        return '''<h5>You can only upload a PDF.</h5>
                <p><a href="''' + index_page + '">Upload another file</a></p>'

if __name__ == '__main__':
    app.run()

