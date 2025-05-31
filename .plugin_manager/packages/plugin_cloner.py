# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Python
import re

# Site-package
from git import Repo
import requests

# Package
from common.constants import (
    PLUGIN_LIST,
    START_DIR,
    config,
)
from common.functions import clear_screen

# ==============================================================================
# >> GLOBAL VARIABLES
# ==============================================================================
repo_url = (
    "https://api.github.com/users/{author}/repos"
    "?per_page={per_page}&page={page}"
)
orgs_url = "https://api.github.com/orgs/{org}/repos"
per_page = 30

ORGANIZATIONS = config["ORGANIZATIONS"]
if isinstance(ORGANIZATIONS, str):
    ORGANIZATIONS = [ORGANIZATIONS]
ORGANIZATIONS = set(ORGANIZATIONS)

MATCH_TOPICS = config["MATCH_TOPICS"]
if isinstance(MATCH_TOPICS, str):
    MATCH_TOPICS = [MATCH_TOPICS]
MATCH_TOPICS = set(MATCH_TOPICS)

EXCLUDE_TOPICS = config["EXCLUDE_TOPICS"]
if isinstance(EXCLUDE_TOPICS, str):
    EXCLUDE_TOPICS = [EXCLUDE_TOPICS]
EXCLUDE_TOPICS = set(EXCLUDE_TOPICS)

CONVERSIONS = config["CONVERSIONS"]


# ==============================================================================
# >> CLASSES
# ==============================================================================
class RepoCloner(dict):
    def __init__(self):
        super().__init__()
        self.populate_list_from_user()
        self.populate_list_from_organizations()

    def populate_plugin_list(self, url):
        page = 0
        while True:
            page += 1
            current_url = url.format(
                author=config["AUTHOR"],
                per_page=per_page,
                page=page,
            )
            response = requests.get(
                url=current_url,
                headers={"User-Agent": "PluginManager"},
            )
            if response.status_code != 200:
                print(
                    f"Error retrieving plugin list for {current_url}:"
                    f" {response.status_code}"
                )
                break

            items = response.json()
            for item in items:
                if item["fork"] or item["archived"]:
                    continue

                topics = set(item["topics"])
                if set(EXCLUDE_TOPICS).intersection(topics):
                    continue

                if topics.intersection(set(MATCH_TOPICS)) != MATCH_TOPICS:
                    continue

                name = item["name"]
                for old, new in CONVERSIONS.items():
                    name = name.replace(old, new)

                name = "_".join(filter(None, re.split(r"(?=[A-Z])", name))).lower()
                if name in PLUGIN_LIST:
                    continue

                self[name] = item["ssh_url"]

            if len(items) < per_page:
                break

    def populate_list_from_user(self):
        self.populate_plugin_list(url=repo_url)

    def populate_list_from_organizations(self):
        for org in ORGANIZATIONS:
            self.populate_plugin_list(url=orgs_url.format(org=org))

    def get_choice(self):
        clear_screen()
        message = "Choose a plugin to clone:\n\n"
        for index, key in enumerate(sorted(self), start=1):
            message += f"{index}. {key}\n"

        value = None
        while True:
            try:
                value = input(message)
                choice_index = int(value)
                assert 0 < choice_index <= len(self)
            except (ValueError, AssertionError):
                print(f"Invalid choice '{value}'. Please try again.")
            else:
                return sorted(self)[choice_index - 1]

    def clone_plugin(self, plugin):
        Repo.clone_from(self[plugin], START_DIR / plugin)


# ==============================================================================
# >> CALL MAIN FUNCTION
# ==============================================================================
if __name__ == "__main__":
    _cloner = RepoCloner()
    if _cloner:
        _plugin = _cloner.get_choice()
        _cloner.clone_plugin(_plugin)
    else:
        print("No plugins found.")
