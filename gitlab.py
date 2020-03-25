import json
import urllib.request
import slack
from datetime import datetime

SLACK_TOKEN = "xoxb-982408464804-1022666434166-n1nL5VKSnf7y5jjF4eCldyzc"
SLACK_CHANNEL = "testing"

# SLACK_TOKEN = "xoxb-3455196592-1024244378391-DumK7c18gvDTHFrbN451eoEu"
# SLACK_CHANNEL = "bot-test"

GITLAB_TOKEN = "xccu1ekNJrMHR1GP-9L9"
PROJECT_URL = "https://gitlab.bouncex.net/api/v4/projects/{id}?private_token={gitlabToken}"
MR_URL = "https://gitlab.bouncex.net/api/v4/projects/{id}/merge_requests?state=opened&wip=no&order_by=updated_at&private_token={gitlabToken}"

groups = {17: []}
now = datetime.utcnow()


def test():
    for k,v in groups.items():
        print(f"{k}-{v}")


def ellipsify(str, maxl):
    if len(str) > maxl:
        return str[0:maxl] + "..."
    else:
        return str


def get_json(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    data = response.read().decode('utf-8')
    return json.loads(data)


def format_mr(v):
    updated = datetime.strptime(v['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
    days_ago = (now - updated).days
    return "<{url}|{title}>\n{author} - _last updated {updatedDays} ago_".format(
        title=ellipsify(v['title'], 75).ljust(55, ' '),
        author=v["author"]["name"],
        url=v["web_url"],
        updatedDays=f"{days_ago} days" if days_ago > 0 else "less than 1 day")


def main():
    blocks = [{"type": "section",
               "text": {"type": "mrkdwn", "text": "_Hot, non WIP MRs in your area, waiting to get reviewed_ :lips:"}}]
    for id in groups:
        project = PROJECT_URL.format(id=id, gitlabToken=GITLAB_TOKEN)

        mrs = MR_URL.format(id=id, gitlabToken=GITLAB_TOKEN)

        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": "\n*{name}*".format(name=get_json(project)['name'])}})
        blocks.append({"type": "divider"})

        ready_to_review = [j for j in get_json(mrs) if not j["work_in_progress"]]

        if len(ready_to_review) != 0:
            for v in ready_to_review:
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": format_mr(v)}})
        else:
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "No MRs"}})

    client = slack.WebClient(token=SLACK_TOKEN)

    # testing
    if 1 == 1:
        client.chat_postMessage(
            channel=SLACK_CHANNEL,
            blocks=blocks
        )


test()
