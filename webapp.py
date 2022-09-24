from flask import Flask, render_template, request
import json
import os
import requests
app = Flask(__name__)

def get_state():
    api_key = os.environ['OPNSENSE_API_KEY']
    api_secret = os.environ['OPNSENSE_API_SECRET']
    url = 'https://%s/api/unbound/settings/get' % os.environ['OPNSENSE_API_HOSTNAME']

    r = requests.get(url, verify=False, auth=(api_key, api_secret))

    if r.status_code == 200:
        response = json.loads(r.text)
        if response["unbound"]["dnsbl"]["enabled"] == "1":
            return "AdBlock is Enabled"
        else:
            return "AdBlock is Disabled"
    else:
        return "ERROR! Unable to retrieve current state."

def adblock(enable):
    succeed = False
    output = ""
    api_key = os.environ['OPNSENSE_API_KEY']
    api_secret = os.environ['OPNSENSE_API_SECRET']                                                 
    url = 'https://%s/api/unbound/settings/set' % os.environ['OPNSENSE_API_HOSTNAME']
    apply_url = "https://%s/api/unbound/service/dnsbl" % os.environ['OPNSENSE_API_HOSTNAME']
    headers = {'content-type': 'application/json'}
    setting = '{"unbound":{"dnsbl":{"enabled":"%s","type":"aa,ag,sa,st","lists":"","whitelists":""},"miscellaneous":{"privatedomain":"","insecuredomain":""}}}' % int(enable)
    
    r = requests.post(url,
                     verify=False,
                     data=setting,
                     auth=(api_key, api_secret),
                     headers=headers)

    output += str(r.text) + "\n"
    
    if r.status_code == 200:
        succeed = True
        r = requests.post(apply_url,
                         data='',
                         verify=False,
                         auth=(api_key, api_secret))

        output += str(r.text) + "\n"

        if r.status_code == 200:
            succeed = True
        else:
            succeed = False
    else:
        succeed = False

    return succeed, output

@app.route("/", methods=['GET', 'POST'])
def index(form=None, output="", status=None):
    if request.method == 'POST':
        if request.form.get('disable') == 'disable':
            succeed, output = adblock(False)
        elif  request.form.get('enable') == 'enable':
            succeed, output = adblock(True)
        else:
            pass # unknown

        if succeed:
            status = "SUCCESS"
        else:
            status = "FAILED!"

    elif request.method == 'GET':
        return render_template('index.html', form=form, state=get_state())
    
    return render_template("index.html", state=get_state(), status=status, output=output)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)
