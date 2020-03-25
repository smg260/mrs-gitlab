import json
import urllib.request
import slack
from datetime import datetime

SLACK_TOKEN = "<token>"
SLACK_CHANNEL = "<channel>"

GITLAB_TOKEN = "<gitlab token>"
PROJECT_URL = "https://<your_host_here>/api/v4/projects/{id}?private_token={gitlabToken}"
MR_URL = "https://<your_host_here>/api/v4/projects/{id}/merge_requests?state=opened&wip=no&order_by=updated_at&private_token={gitlabToken}"

#from gitlab
groups = [87, 256, 26, 25, 45]
groups.sort()
now = datetime.utcnow()


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


main()
