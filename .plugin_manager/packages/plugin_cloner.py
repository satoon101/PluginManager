# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import re

# Site-package
import requests

# Package
from common.constants import (
    PLUGIN_LIST,
    START_DIR,
    config,
)
from common.interface import BaseInterface

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
repo_url = (
    "https://api.github.com/users/{author}/repos"
    "?per_page={per_page}&page={page}"
)
orgs_url = "https://api.github.com/orgs/{org}/repos"
per_page = 30

ORGANIZATIONS = config["ORGANIZATIONS"]
if ORGANIZATIONS and isinstance(ORGANIZATIONS, str):
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


# =============================================================================
# >> CLASSES
# =============================================================================
class Interface(BaseInterface):

    name = "Plugin Cloner"
    repos = {}

    def run(self, plugin_name=None):
        self.window.title(self.name)
        self.clear_grid()
        if not self.repos:
            self.populate_repos_from_user()
            self.populate_repos_from_organizations()

        if plugin_name and (START_DIR / plugin_name).is_dir():
            del self.repos[plugin_name]

        self.create_grid(data=self.repos)
        self.add_back_button(self.on_back_to_main)

    def identify_repos(self, url):
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

                name = "_".join(
                    filter(
                        None,
                        re.split(r"(?=[A-Z])", name)
                    )
                ).lower()
                if name in PLUGIN_LIST:
                    continue

                self.repos[name] = item["ssh_url"]

            if len(items) < per_page:
                break

    def populate_repos_from_user(self):
        self.identify_repos(url=repo_url)

    def populate_repos_from_organizations(self):
        for org in ORGANIZATIONS:
            self.identify_repos(url=orgs_url.format(org=org))

    def on_click(self, option):
        self.clear_grid()
        console = self.get_console()
        self.execute_console_commands(
            console=console,
            commands=[f"git clone {self.repos[option]} {START_DIR / option}"]
        )
        self.add_back_button(lambda o=option: self.run(plugin_name=o))
