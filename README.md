# steamfriendsgraph

## How it works

- friends list is scraped from steamhistory
- this list is further used to get friends of friends
- graph is generated where users are nodes and friendships are edges

## Usage

- clone the repository
- install requirements with `pip install -r requirements.txt`
- run the script with `python friendslist.py`
- a graph will be generated and saved as `./graph.graphml`

## Further usage

- the graphml file can be opened with a tool like Gephi for further visualisation or analysis
- networkx object in python can be used conveniently for further scripting and analysis
- all pages fetched are stored in `./cache/` can be used for extracting more information
