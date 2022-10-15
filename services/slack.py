from urllib.request import Request, urlopen
import json
import os


class Slack:
    def send_message_to_slack(self, title, text):
        post = { "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "\n*Server_id*:" + os.environ['INSTANCE_ID'] + "\n*Title*:" + title + "\n```" + str(text) + "```"
                            }
                        }
                    ]
                }
        try:
            json_data = json.dumps(post)
            web_hook = os.environ.get('NOTIFICATION_SLACK_WEB_HOOK')
            print("web_hook:: ", web_hook.__str__())
            req = Request(web_hook.__str__(), data=json_data.encode('ascii'), headers={'Content-Type': 'application/json'})
            resp = urlopen(req)
            print(resp)
        except Exception as em:
            print("EXCEPTION: " + str(em))