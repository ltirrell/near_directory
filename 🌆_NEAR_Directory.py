import pandas as pd
import streamlit as st


from near.utils import get_user_query
from near.gov import get_validators

st.set_page_config(
    page_title="NEAR Directory - Your guide to the City of NEAR",
    page_icon="🌆",
    layout="wide",
)

pd.options.display.max_colwidth = 1000000  # needed to print string properly for TX
st.title("NEAR Directory")

st.write(
    f"""
Welcome to the NEAR Directory, your guide to the City of [NEAR](https://near.org/)!

Flip through the Directory here, or visit one of the landmarks for a tour of what NEAR has to offer through a link in the sidebar or here:
- [NFTs: Arts District](Arts_District): a walk through the NFT scene of NEAR, focusing on [Paras](https://paras.id/)
- [DeFi: Financial District](Financial_District): an inspection of the *de facto* Central Bank of Near, [Ref Finance](https://ref.finance/)
- [Validators: Local Government](Local_Government): a view of the NEAR politics, taking a closer look at its validators
- [Crosschain/New Users: User Journey](User_Journey): an overview of how users start on the NEAR blockchain

Data is provided by [Flipside Crypto](https://flipsidecrypto.xyz/) and other sources. See the Methods sections of each page for details.
    """
)

st.header("Address lookup")
st.write("Search the Near Directory Rolodex by entering an address below.")
st.caption("Note: this is a Work in Progress, and more information will become available in the future!")


address = st.text_input("Near Address:")
if address:
    if not address.endswith(".near") and len(address) != 64:
        st.write("Invalid NEAR address, please try entering another.")
    else:
        query_state = st.text("Loading data from Flipside Crypto...")
        df = get_user_query(address)
        success_df = df[df.TX_STATUS == "Success"].copy()
        query_state.text("")

        c1, c2, c3, c4 = st.columns(4)

        n_tx = len(df)

        success_tx = len(success_df)
        fail_tx = n_tx - success_tx
        success_rate = success_tx / n_tx

        c1.metric("Number of transactions", n_tx)
        c2.metric("Successful transactions", success_tx)
        c3.metric("Failed transactions", fail_tx)
        c4.metric("Success Rate", f"{success_rate:.1%}")

        unique_receivers = success_df.TX_RECEIVER.unique()
        n_receivers = len(unique_receivers)
        c1.metric("Unique contract interactions", n_receivers)

        marketplace_tx = success_df[success_df.TX_RECEIVER == "marketplace.paras.near"]
        n_nft_tx = len(marketplace_tx)
        c2.metric("NFT marketplace transactions (Paras)", n_nft_tx)

        ref_df = success_df.copy()
        ref_df["tx_string"] = ref_df.TX.apply(str)
        ref_tx = ref_df[ref_df.tx_string.str.contains("v2.ref-")]
        n_ref_tx = len(ref_tx)
        c3.metric("DeFI transactions (Ref)", n_ref_tx)

        validators_df = get_validators()
        stake_tx = success_df[success_df.TX_RECEIVER.isin(validators_df.account_id)]
        n_staking_tx = len(stake_tx)
        c4.metric("NEAR staking/unstaking transactions", n_staking_tx)


# st.subheader("Methods")
# with st.expander("Methods and Data Sources"):
#     st.write("here are some methods")
