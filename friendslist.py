import os
import json

import time

import requests
from bs4 import BeautifulSoup
# from pyvis.network import Network

import networkx as nx


def init_cache():
    os.makedirs("cache", exist_ok=True)


def test_url(url):
    is_steamhistory_url = url.startswith("https://steamhistory.net/id/")
    if not is_steamhistory_url:
        raise ValueError("Not a valid steam url")


def cached_request_steamhistory(url):
    user_id = url[27:]
    cache_path = "cache/" + user_id
    # TODO: replace with regex

    if os.path.exists(cache_path):
        print(f"found cached source for {user_id}")
        with open(cache_path) as f:
            return f.read()

    else:
        print(f"fetching {url}")
        r = requests.get(url)
        source = r.content
        if "Please wait while it is indexed" in str(source):
            print("*" * 10, "Waiting 1s for profile to get indexed", "*" * 10)
            time.sleep(1)
            return cached_request_steamhistory(url)
        print(source)
        r.raise_for_status()

        with open(cache_path, "w+") as f:
            f.write(str(source))

        return source


def get_steam_profile_source(url):
    test_url(url)
    return cached_request_steamhistory(url)


def get_soup(source):
    soup = BeautifulSoup(source, features="html.parser")
    return soup


def getfriendslist(url):
    source = get_steam_profile_source(url)
    soup = get_soup(source)
    friends_elements = soup.select(
        "div.col:nth-child(3) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(2) > tr > td:nth-child(1) > a:nth-child(1)"
    )

    friends_usernames = list(map(lambda x: x.text, friends_elements))
    friends_ids = list(
        map(
            lambda x: x["href"][30:-2],
            friends_elements,
        )
    )
    friends = dict(zip(friends_ids, friends_usernames))

    return friends


def get_steamhistory_url(target_id):
    return f"https://steamhistory.net/id/{target_id}"


def add_friends_to_graph(target_id, target_username, net):
    friends = getfriendslist(get_steamhistory_url(target_id))
    print(json.dumps(friends, indent=4))
    net.add_node(target_id, label=target_username)
    for friend_id, friend_username in friends.items():
        net.add_node(
            friend_id, label=friend_username, url=get_steamhistory_url(
                friend_id)
        )
        net.add_edge(target_id, friend_id)
    return friends


# def generate_pyvis_graph(target_id, target_username):
#     net = Network()
#
#     friends = add_friends_to_graph(target_id, target_username, net)
#     for friend_id, friend_name in friends.items():
#         add_friends_to_graph(friend_id, friend_name, net)
#
#     net.show_buttons()
#     net.show("friends.html", notebook=False)
#     return net


def generate_graphml(target_id, target_username):
    G = nx.Graph()
    G.add_node(target_id, label=target_username,
               url=get_steamhistory_url(target_id))
    friends = add_friends_to_graph(target_id, target_username, G)
    for friend_id, friend_name in friends.items():
        add_friends_to_graph(friend_id, friend_name, G)

    nx.write_graphml(G, "graph.graphml")
    print("wrote graph to graph.graphml")
    return friends


# def test():
#     net = Network()
#
#     net.add_node("A", label="Node A")
#     net.add_node("B", label="Node B")
#     net.add_edge("A", "B", title="A to B")
#
#     net.show("test_graph.html", notebook=False)


if __name__ == "__main__":
    init_cache()
    generate_graphml(
        target_id=input("Enter steam id: "),
        target_username=input("Enter central node name (target username): "),
    )
    print("tip: use a graphml viewer like Gephi to analyze the graph.")
    exit(0)
