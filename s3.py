'''
You need to have AWS credentials in ~/.aws/credentials
[default]
aws_access_key_id=KEY_ID
aws_secret_access_key=ACCESS_KEY

pip install boto3
'''

from flask import Flask, flash, request, render_template, redirect
from livereload import Server, shell
import boto3

ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)

# remember to use DEBUG mode for templates auto reload
# https://github.com/lepture/python-livereload/issues/144
app.debug = True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 's3file' not in request.files:
        flash('Something went wrong. No file found')
        return redirect(request.url)

    if request.files['s3file'].filename == '':
        flash('No file selected')

    if request.files['s3file'] and allowed_file(request.files['s3file'].filename):
	# Uncomment below client call with aws_access_key_id and aws_secret_access_key if no credentials file in .aws folder. --FOR TESTING ONLY. Insecure to include in code.
	# Don't forget to comment out the client call with only "s3".
        # s3 = boto3.client(
        #     "s3",
        #     aws_access_key_id='[ACCESS_KEY]',
        #     aws_secret_access_key='[SECRET_KEY]'
        # )
        s3 = boto3.client("s3")

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
                <p><a href="/">Upload another file</a></p>'''
    else:
        return '''<h5>You can only upload a PDF.</h5>
                <p><a href="/">Upload another file</a></p>'''

# if __name__ == '__main__':
#     app.run(debug=True)

# Live reload server
# Prob want to set some sort of env flag to only do this on DEV
server = Server(app.wsgi_app)

# use custom host and port
server.serve(port=80, host='0.0.0.0')
