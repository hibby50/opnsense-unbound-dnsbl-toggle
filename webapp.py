from flask import Flask, render_template, request
import json
import os
import requests
app = Flask(__name__)

class OpensenseAdblock:
    def __init__(self, url=os.environ['OPNSENSE_API_HOSTNAME'], api_key=os.environ['OPNSENSE_API_KEY'], api_secret=os.environ['OPNSENSE_API_SECRET']):
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret

    def get_blocklists(self):
        settings_url = f"{self.url}/api/unbound/settings/search_dnsbl"
        r = requests.post(settings_url,
                            verify=False,
                            auth=(self.api_key, self.api_secret))
        r.raise_for_status()

        data = r.json()
        return data.get('rows', [])

    def get_state(self):
        blocklists = {}
        for row in self.get_blocklists():
            status = "ENABLED" if row.get('enabled') == "1" else "DISABLED"
            blocklists[row.get('uuid')] = f"{status}: {row.get('description', 'No description')} - {row.get('%type')}"

        return f"{'\n'.join(blocklists.values())}\n\n"

    def change_blocklist(self, enable, uuids):
        for uuid in uuids:
            settings_url = f"{self.url}/api/unbound/settings/toggle_dnsbl/{uuid}/{int(enable)}"
            r = requests.post(settings_url,
                            verify=False,
                            auth=(self.api_key, self.api_secret))
            r.raise_for_status()
        return r.text

    def apply_changes(self):
        apply_url = f"{self.url}/api/unbound/service/dnsbl"
        r = requests.post(apply_url,
                            data='',
                            verify=False,
                            auth=(self.api_key, self.api_secret))
        r.raise_for_status()
        return r.text

    def adblock(self, enable):
        blocklist_uuids = []
        for row in self.get_blocklists():
            blocklist_uuids.append(row.get('uuid'))

        change = self.change_blocklist(enable, blocklist_uuids)
        output = f"Change blocklist settings: {change}\n"
        if json.loads(change)['changed']:
            output += f"Apply blocklist settings: {self.apply_changes()}\n"
        else:
            output+= "No change made, not applying"

        return output

@app.route("/", methods=['GET', 'POST'])
def index(form=None, output="", status=None):
    status = "Unknown"
    opnsense_adblock = OpensenseAdblock()
    if request.method == 'POST':
        try:
            status = "SUCCESS"
            if request.form.get('disable') == 'disable':
                output = opnsense_adblock.adblock(False)
            elif  request.form.get('enable') == 'enable':
                output = opnsense_adblock.adblock(True)
            else:
                status = "Unknown"
                pass # unknown
        except requests.exceptions.HTTPError as e:
            status = "API error encountered"
            output = e
        except Exception as e:
            status = "Exception Occured"
            output = e

    elif request.method == 'GET':
        return render_template('index.html', form=form, state=opnsense_adblock.get_state())
    
    return render_template("index.html", state=opnsense_adblock.get_state(), status=status, output=output)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
