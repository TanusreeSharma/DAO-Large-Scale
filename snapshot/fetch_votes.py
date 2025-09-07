import requests
import csv
import time


import requests


def get_proposal(space_id):
    print(f"Fetching proposals for {space_id}")
    # Define the GraphQL query
    query = f"""
    query {{
        proposals (
            first: 1000,
            skip: 0,
            where: {{
                space: "{space_id}",
                state: "closed"
            }},
            orderBy: "created",
            orderDirection: desc
        ) {{
            id
            author
        }}
    }}
    """
    while True:
        # Send the GraphQL request
        response = requests.post(
            "https://hub.snapshot.org/graphql", json={"query": query}
        )

        # Check if the request was successful
        if response.status_code == 200:
            # Retrieve the data from the response
            data = response.json()["data"]
            proposals = data["proposals"]

            # Extract and return the proposal IDs as a list
            proposal_ids_authors = [
                (proposal["id"], proposal["author"]) for proposal in proposals
            ]
            return proposal_ids_authors


def fetch_votes(space_id="yam.eth", delay=1):
    # Retrieve the proposal IDs
    proposal_ids = get_proposal(space_id)
    print(proposal_ids)
    first = True
    # Loop through the proposal IDs
    print(f"Fetching votes for {space_id}")
    for proposal in proposal_ids:
        proposal_id = proposal[0]
        proposal_author = proposal[1]
        skip = 0
        while True:
            # Wait delay second before sending the request
            time.sleep(delay)
            # Define the GraphQL query
            query = f"""
            query {{
            votes (
                first: 1000,
                skip: {skip},
                where: {{
                proposal: "{proposal_id}"
                }},
                orderBy: "created",
                orderDirection: desc
            ) {{
                id
                voter
                vp
                created
                proposal {{
                id
                author
                }}
                choice
            }}
            }}
            """

            # Send the GraphQL request
            response = requests.post(
                "https://hub.snapshot.org/graphql", json={"query": query}
            )

            # Check if the request was successful
            if response.status_code == 200:
                # Retrieve the data from the response
                data = response.json()["data"]
                votes = data["votes"]
                if votes == []:
                    break

                # Save the results in a CSV file
                with open(
                    f"data/votes/{space_id.replace('.','_')}.csv",
                    mode="a",
                    newline="",
                ) as file:
                    writer = csv.writer(file)
                    if first:
                        writer.writerow(
                            [
                                "vote_id",
                                "address",
                                "voting_power",
                                "timestamp",
                                "proposal_id",
                                "choice",
                                "proposal_author",
                            ]
                        )
                        first = False

                    # Write each vote as a row in the CSV file
                    for vote in votes:
                        row = [
                            vote["id"],
                            vote["voter"],
                            vote["vp"],
                            vote["created"],
                            vote["proposal"]["id"],
                            vote["choice"],
                            vote["proposal"]["author"],
                        ]
                        writer.writerow(row)
                    print(len(votes))
                    if len(votes) < 1000:
                        break

                # print("Results saved in votes.csv")
                skip += 1000
            else:
                print(f"Error: {response.status_code} - {response.text}")
                print(f"Space: {space_id}")
                print(f"Skip: {skip}")
                0 / 0


all_space_ids = ["golflinks.eth", "macaronswap.eth", "loopringdao.eth"]
for space_id in all_space_ids:
    fetch_votes(space_id=space_id, delay=1)
