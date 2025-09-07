import requests
from web3 import Web3
import json


def fetch_space_data(space_id):
    endpoint = "https://hub.snapshot.org/graphql"
    query = f"""
    query {{
  space(id: "{space_id}") {{
    strategies {{
      network
      params
    }}
  }}
}}
    """

    response = requests.post(endpoint, json={"query": query})
    data = response.json()

    strategies = data["data"]["space"]["strategies"]
    print(strategies)
    if strategies:
        strategy = strategies[0]
        network = strategy["network"]
        params = strategy["params"]
        address = params["address"]
        decimals = params["decimals"]
        try:
            methodABI_name = params["methodABI"]["name"]
        except KeyError:
            methodABI_name = "balanceOf"

        try:
            return (
                network,
                address,
                decimals,
                methodABI_name,
                [params["methodABI"]],
            )
        except:
            # read erc20 abi from json

            with open("abi/erc20.json") as f:
                methodABI = json.load(f)
            return network, address, decimals, methodABI_name, methodABI


def fetch_token_value(
    user_address,
    network,
    token_address,
    decimals,
    methodABI_name,
    block_number,
    methodABI,
):
    block_number = int(block_number)
    # Initialize web3 object based on the specified network
    if network == "1":  # Ethereum mainnet
        web3 = Web3(
            Web3.HTTPProvider(
                "https://eth-mainnet.g.alchemy.com/v2/itNT-7Uc7W4wt1BFYk381Bg-gQA9Gxj0"
            )
        )
    elif network == "56":  # Binance Smart Chain mainnet
        web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.defibit.io"))
    elif network == "137":  # Polygon mainnet
        web3 = Web3(
            Web3.HTTPProvider(
                "https://polygon-mainnet.g.alchemy.com/v2/7DjhoRhOoizDci3-DGLjtsoZBI-aNlpZ"
            )
        )
    else:
        print(network, token_address, "Network not supported.")
        0 / 0
        return None

    # Create the contract instance using the token address and ABI
    contract = web3.eth.contract(
        address=web3.toChecksumAddress(token_address), abi=methodABI
    )

    # Call the methodABI_name on the contract, passing in the user's address as a parameter
    token_balance = contract.functions[methodABI_name](user_address).call(
        block_identifier=block_number
    )

    # Calculate the value divided by 10^decimals
    value = token_balance / 10**decimals
    return value


import csv


def get_proposals(space_id):
    (
        network,
        token_address,
        decimals,
        methodABI_name,
        methodABI,
    ) = fetch_space_data(space_id)

    endpoint = "https://hub.snapshot.org/graphql"
    query = (
        """
    query {
      proposals (
        first: 1000,
        skip: 0,
        where: {
          space_in: ["%s"]
        },
        orderBy: "created",
        orderDirection: desc
      ) {
        id
        choices
        snapshot
        state
        scores
        scores_total
        author
      }
    }
    """
        % space_id
    )

    response = requests.post(endpoint, json={"query": query})
    data = response.json()

    try:
        proposals = data["data"]["proposals"]
        if proposals:
            with open(
                f"data/proposals/{space_id.replace('.', '_')}.csv",
                "w",
                newline="",
            ) as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        "ID",
                        "Author",
                        "State",
                        "BlockNumber" "Choices",
                        "Scores",
                        "AuthorTokenBalance",
                    ]
                )

                for proposal in proposals:
                    proposal_id = proposal["id"]
                    choices = proposal["choices"]
                    state = proposal["state"]
                    scores = proposal["scores"]
                    author = proposal["author"]
                    start = proposal["snapshot"]

                    token_balance = fetch_token_value(
                        author,
                        network,
                        token_address,
                        decimals,
                        methodABI_name,
                        start,
                        methodABI,
                    )

                    writer.writerow(
                        [
                            proposal_id,
                            author,
                            state,
                            start,
                            choices,
                            scores,
                            token_balance,
                        ]
                    )

            print(
                f"Proposals data written to {space_id.replace('.', '_')}.csv."
            )
        else:
            print("No proposals found.")
    except KeyError:
        print("Error retrieving proposals.")


# Example usage:
space_ids = ["uniswap", "cakevote.eth"]
for space_id in space_ids:
    print(space_id)
    get_proposals(space_id)
