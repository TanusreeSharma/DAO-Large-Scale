import pandas as pd
import numpy as np

np.random.seed(20240123)  # fixed seed for reproducibility

# Load exported candidate list
df = pd.read_csv("candidate_list.csv")

# Stratification mappings
type_map = {
    "defi":"DeFi", "dex":"DeFi", "lending":"DeFi",
    "investment":"Investment", "dao tool":"Tooling", "nft":"NFT",
    "research":"Research", "social":"Social", "gaming":"Gaming",
    "public goods":"PublicGoods", "governance":"Governance"
}
df["type_stratum"] = df["type_raw"].str.lower().map(type_map).fillna("Other")

# Treasury bins (USD):
bins = [-1, 1e6, 10e6, 100e6, np.inf]
labels = ["0-1M", "1-10M", "10-100M", "100M+"]
df["treasury_stratum"] = pd.cut(df["treasury_usd"], bins=bins, labels=labels)

# Voting module mapping:
vm_map = {"snapshot":"Snapshot", "aragon":"OnChain", "onchain":"OnChain",
          "governor":"OnChain", "manual":"Other", "discord":"Other"}
df["voting_module_stratum"] = df["voting_module_raw"].str.lower().map(vm_map).fillna("Other")

# Token nature:
df["token_nature_stratum"] = np.where(df["has_secondary_market"], "Monetary", "NonMonetary")

# Save strata assignments
df[["dao_id", "type_stratum", "treasury_stratum", "voting_module_stratum", "token_nature_stratum"]].to_csv("strata_assignments.csv", index=False)

# Stratified sampling: proportionate draw to 100 DAOs
cross = df.groupby(["type_stratum", "treasury_stratum", "voting_module_stratum", "token_nature_stratum"]).size().reset_index(name="count")
cross["alloc"] = np.floor(cross["count"] / cross["count"].sum() * 100).astype(int)

samples = []
for _, row in cross.iterrows():
    subset = df[
        (df["type_stratum"] == row["type_stratum"]) &
        (df["treasury_stratum"] == row["treasury_stratum"]) &
        (df["voting_module_stratum"] == row["voting_module_stratum"]) &
        (df["token_nature_stratum"] == row["token_nature_stratum"])
    ]
    n = min(len(subset), row["alloc"])
    if n > 0:
        samples.append(subset.sample(n=n, random_state=20240123))

sampled = pd.concat(samples, ignore_index=True)
if len(sampled) < 100:
    remaining = df[~df["dao_id"].isin(sampled["dao_id"])]
    probs = remaining.shape[0] / remaining.shape[0]
    supplemental = remaining.sample(n=100 - len(sampled), random_state=20240123, weights=None)
    sampled = pd.concat([sampled, supplemental], ignore_index=True)

sampled.to_csv("sample_100_daos.csv", index=False)
