import streamlit as st

from near.utils import get_user_query


st.set_page_config(
    page_title="NEAR Directory - Your guide to the City of NEAR",
    page_icon="🌆",
    layout="wide",
)
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


address = st.text_input("Near Address:")
query_state = st.text("Loading data from Flipside Crypto...")
df = get_user_query(address)
query_state.text("")
c1, c2 = st.columns(2)
c1.metric("Number of transactions", len(df))

# st.subheader("Methods")
# with st.expander("Methods and Data Sources"):
#     st.write("here are some methods")
