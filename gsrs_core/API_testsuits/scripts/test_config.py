# [URL]
#SERVER_URL="http://gsrs-uat.preprod.fda.gov/"
SERVER_URL = "http://localhost:8080/"
headerspost = {'auth-key':"your_key",'auth-username':'your_login', 'content-type': 'text/plain'}

# [input and output]
input_path="../input/"
output_path="../output/"

# [Security]
# Please change verify to False if you do not need verification during test.
# verify=False
verify_flag=True