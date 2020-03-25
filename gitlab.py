import json
import urllib.request
import slack
from datetime import datetime

# dr
SLACK_TOKEN = "<slack token>"

GITLAB_HOST = "<gitlab host>"
GITLAB_TOKEN = "<gitlab token>"

GROUP_URL = "https://{gitlab_host}/api/v4/groups/{id}?private_token={token}"
MR_PARAMS = "state=opened&wip=no&order_by=updated_at"

# the token being used must originate from a user who has permissions to the specified groups
# if a whitelist, then only those are considered, otherwise all in the group
configs = [{"group_id": 17, "channels": ["testing"]}]
now = datetime.utcnow()


def ellipsify(str, maxl):
    if len(str) > maxl:
        return str[0:maxl] + "..."
    else:
        return str


def get_json(url):
    print(url)
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    data = response.read().decode('utf-8')
    return json.loads(data)


def format_mr(v):
    updated = datetime.strptime(v['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
    days_ago = (now - updated).days
    return "<{url}|{title}>\n{author} - _last updated {updatedDays} ago_\n\n".format(
        title=ellipsify(v['title'], 75).ljust(55, ' '),
        author=v["author"]["name"],
        url=v["web_url"],
        updatedDays=f"{days_ago} days" if days_ago > 0 else "less than 1 day")


def format_mrs(mrs):
    str = ""
    for v in mrs:
        str += format_mr(v)
    return str


def main():
    client = slack.WebClient(token=SLACK_TOKEN)
    for c in configs:
        group = get_json(GROUP_URL.format(id=c["group_id"], gitlab_host=GITLAB_HOST, token=GITLAB_TOKEN))
        blocks = [{"type": "section",
                   "text": {"type": "mrkdwn",
                            "text": "_Hot, non WIP MRs in {group_name}, waiting to get reviewed_ :lips:".format(
                                group_name=group["name"])}}]
        for project in [p for p in sorted(group["projects"], key=lambda p: p["name"].lower()) if
                        "whitelist" not in c or p["id"] in c["whitelist"]]:
            mrs = get_json(
                "{mr_url}?private_token={token}&{mr_params}".format(mr_url=project["_links"]["merge_requests"],
                                                                    mr_params=MR_PARAMS, token=GITLAB_TOKEN))
            ready_to_review = [j for j in mrs if not j["work_in_progress"]]

            if len(ready_to_review) != 0:
                blocks.append(
                    {"type": "section", "text": {"type": "mrkdwn", "text": "*{name}*\n\n{formatted_mrs}".format(
                        name=project['name'], formatted_mrs=format_mrs(ready_to_review))}})
                blocks.append({"type": "divider"})

        # testing
        if 1 == 1:
            for ch in c["channels"]:
                print("slacking ...")
                client.chat_postMessage(
                    channel=ch,
                    blocks=blocks
                )


main()
