import io
import os
import random

import altair as alt
import pandas as pd
import requests
from shroomdk import ShroomDK, errors
import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Citizens of NEAR: Arts District", page_icon="🌆", layout="wide"
)
st.title("Citizens of NEAR: Arts District")
st.caption(
    """
What is a city without a thriving center for arts and culture?!

Exploring the NEAR NFT scene.
"""
)


API_KEY = os.getenv("SHROOMDK_KEY")


@st.cache(ttl=24 * 60)
def get_flipside_data(query, cached=True, save=False):
    query_result_set = sdk.query(query, cached=cached)
    df = pd.DataFrame(query_result_set.rows, columns=query_result_set.columns)
    if save:
        df.to_csv("query.csv")
    return df


@st.cache(ttl=24 * 60)
def load_data():
    sales_volume_df = pd.read_json(
        "https://node-api.flipsidecrypto.com/api/v2/queries/6ae95685-436d-4682-8d8b-dec364692ed9/data/latest"
    )
    top_projects_df = pd.read_json(
        "https://node-api.flipsidecrypto.com/api/v2/queries/89c38bbf-9c3b-41d1-a92e-b12d4bdce055/data/latest"
    )
    past_week_df = pd.read_json(
        "https://node-api.flipsidecrypto.com/api/v2/queries/b14104c2-fc26-44fb-9be9-6573b3cf2c00/data/latest"
    )
    top_sales_df = pd.read_json(
        "https://node-api.flipsidecrypto.com/api/v2/queries/a35024bd-71b9-4548-a121-c284c2140fdb/data/latest"
    )
    return sales_volume_df, top_projects_df, past_week_df, top_sales_df


def get_random_collections(n=10, max_num=34270) -> list:
    limit = n
    skip = random.randint(0, max_num)

    r = requests.get(
        "https://api-v2-mainnet.paras.id/collections",
        params={"__limit": limit, "__skip": skip},
    )

    return r.json()["data"]["results"]


def add_collection_stats(collection_data: list) -> list:
    data = []
    for x in collection_data:
        r = requests.get(
            "https://api-v2-mainnet.paras.id/collection-stats",
            params={"collection_id": x["collection_id"]},
        )
        data.append({**x, **r.json()["data"]["results"]})
    return data


def print_stats(x):
    s = ""
    try:
        total_card_sale = x["total_card_sale"]
        total_cards = x["total_cards"]
        s += f"- Total NFTs Minted: {total_cards} ({total_card_sale} listed)\n"
    except:
        pass
    try:
        total_owners = x["total_owners"]
        s += f"- Total Unique Owners: {total_owners}\n"
    except:
        pass
    try:
        volume = x["volume"]
        s += f"- Volume: {int(volume)/10**24:.2f} NEAR\n"
    except:
        pass
    try:
        floor_price = x["floor_price"]
        s += f"- Floor Price: {int(floor_price)/10**24:.2f} NEAR\n"
    except:
        pass
    return s


def alt_line_chart(
    data: pd.DataFrame,
    colname: str = "value",
    log_scale=False,
) -> alt.Chart:
    """Create a multiline Altair chart with tooltip

    Parameters
    ----------
    data : pd.DataFrame
        Data source to use
    colname : str
        Column name for values
    log_scale : str
        Use log scale for Y axis

    Returns
    -------
    alt.Chart
        Chart showing columnname values, and a multiline tooltip on mouseover
    """
    scale = "log" if log_scale else "linear"
    columns = [
        "Most Expensive NFT",
        "Average Sale",
        "Cheapest NFT",
    ]  # hard coding for now...

    base = alt.Chart(
        data,
        title=f"Sale information for NFT collection: {collection_data['collection']} ({col_id})",
    ).encode(
        x=alt.X(
            "yearmonthdate(DATETIME):T",
            axis=alt.Axis(title=""),
        )
    )
    selection = alt.selection_single(
        fields=["DATETIME"],
        nearest=True,
        on="mouseover",
        empty="none",
        clear="mouseout",
    )
    lines = base.mark_area().encode(
        y=alt.Y(
            colname,
            axis=alt.Axis(title="Price (NEAR)"),
            scale=alt.Scale(type=scale),
            stack=None,
        ),
        color=alt.Color(
            "variable:N",
            sort=columns,
            scale=alt.Scale(domain=columns, range=["#404347", "#2eab9c", "magenta"]),
        ),
        # order=alt.Order(columns)
        opacity=alt.value(0.6),
    )

    rule = (
        base.transform_pivot("variable", value=colname, groupby=["DATETIME"])
        .mark_rule()
        .encode(
            opacity=alt.condition(selection, alt.value(0.3), alt.value(0)),
            tooltip=[alt.Tooltip("yearmonthdate(DATETIME)", title="Date")]
            + [
                alt.Tooltip(
                    c,
                    type="quantitative",
                    format=".1f",
                )
                for c in columns
            ],
        )
        .add_selection(selection)
    )
    chart = lines + rule

    return chart.interactive().properties(width=1000)


with st.expander("Methods"):
    st.header("Methods")
    """
    Data was gathered using the [Paras API](https://parashq.github.io/) and Flipside Crypto, based off of this [query](https://app.flipsidecrypto.com/velocity/queries/b4781971-7539-41ef-9c1e-4af08afb79de) from [@pinehearst_](https://twitter.com/pinehearst_).

    The interactive query used for this dashboard can be found [here](https://github.com/ltirrell/flipside_bounties/blob/main/near/arts_district.py#L435), where `col_id` is replaced with the value given by the user.

    The [top NFT projects](https://app.flipsidecrypto.com/velocity/queries/89c38bbf-9c3b-41d1-a92e-b12d4bdce055) and [overall sales volume](https://app.flipsidecrypto.com/velocity/queries/6ae95685-436d-4682-8d8b-dec364692ed9) are updated every 12 hours on Flipside, and are again borrowed from @pinehearst_'s [excellent work](https://app.flipsidecrypto.com/dashboard/near-arts-district-m8p1bd).

    The [top NFT projects in the last 7 days](https://app.flipsidecrypto.com/velocity/queries/b14104c2-fc26-44fb-9be9-6573b3cf2c00) and [most expensive NFT sales](https://app.flipsidecrypto.com/velocity/queries/a35024bd-71b9-4548-a121-c284c2140fdb) are adapted from Discord user `Kaskoazul#4557`'s [dashboard](https://app.flipsidecrypto.com/dashboard/city-of-near-the-arts-district-3nBdeQ)
    """


st.header("What's happening on NEAR?")
st.write(
    "Below is the weekly sale volume of NFTs on NEAR, showing number of sellers, buyers, total sales count and daily volume in NEAR. Sales began to pick up in January 2022, and were quite popular until May 2022, when sales dipped with a market downturn."
)
sales_volume_df, top_projects_df, past_week_df, top_sales_df = load_data()

bars = (
    alt.Chart(
        sales_volume_df,
    )
    .mark_bar(width=10)
    .transform_fold(
        fold=["Sales Count", "Buyers", "Sellers"], as_=["variable", "value"]
    )
    .encode(
        x=alt.X(
            "yearmonthdate(DATE):T",
            axis=alt.Axis(title=""),
        ),
        y=alt.Y("value:Q", title="Sales Count"),
        color=alt.Color("variable:N", legend=alt.Legend(title="Weekly Volume")),
        tooltip=[
            alt.Tooltip("yearmonthdate(DATE)", title="Date"),
            alt.Tooltip(
                "Daily Volume (NEAR)", title="Weekly Volume (NEAR)", format=",.1f"
            ),
            alt.Tooltip("Sales Count"),
            alt.Tooltip("Buyers"),
            alt.Tooltip("Sellers"),
        ],
    )
).interactive()
lines = (
    alt.Chart(
        sales_volume_df,
    )
    .mark_line()
    .transform_fold(
        fold=[
            "Daily Volume (NEAR)",
        ],
        as_=["variable", "value"],
    )
    .encode(
        x=alt.X(
            "yearmonthdate(DATE):T",
            axis=alt.Axis(title=""),
        ),
        y=alt.Y("value:Q", title="Sales Volume (NEAR)"),
        color=alt.Color(
            "variable:N",
            legend=alt.Legend(title=None),
            scale=alt.Scale(
                domain=["Daily Volume (NEAR)"],
                range=[
                    "#474746",
                ],
            ),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdate(DATE)", title="Date"),
            alt.Tooltip(
                "Daily Volume (NEAR)", title="Weekly Volume (NEAR)", format=",.1f"
            ),
            alt.Tooltip("Sales Count"),
            alt.Tooltip("Buyers"),
            alt.Tooltip("Sellers"),
        ],
    )
).interactive()
vol_chart = (
    alt.layer(bars, lines, title="Overall NFT volume on NEAR (weekly)")
    .resolve_scale(y="independent", color="independent")
    .properties(width=1000)
)

st.altair_chart(vol_chart, use_container_width=True)

st.write("The top 50 most expensive NFT sales are shown here, to get an overview of some projects generating the most attention. Most large sales occurred before the May market downturn.")
chart = alt.Chart(top_sales_df).mark_circle(size=50).encode(
    x=alt.X("yearmonthdate(DATETIME)", title=None),
    y=alt.Y("PRICE", title="Price (NEAR)"),
    color=alt.Color("PROJECT", title="NFT Collection"),
    tooltip=[
        alt.Tooltip("yearmonthdate(DATETIME)", title="Sales Date"),
        alt.Tooltip("PROJECT", title="NFT Collection"),
        alt.Tooltip("NFT", title="NFT ID"),
        alt.Tooltip("PRICE", title="Price (NEAR)")
    ]
).interactive().properties(height=500)
st.altair_chart(chart, use_container_width=True)
st.header("The hottest place for art: Paras")
f"""
[Paras](https://paras.id/) is the most popular NFT marketplace on NEAR. Let's take a look at what it has to offer.


"""
st.header("Gallery")
st.write(
    """
Walking through Paras, we see a wide variety of collections.
We can stop to take a look at some. Just press the button!
Note that this may take some time to load...

**NSFW warning: collections are random, and may contain inappropriate images!** We'll hide them by default.
    """
)
col1, col2 = st.columns([3, 1])
n_random = col1.slider("Number of random collections", 1, 10, 4)
if col2.button("Load collections"):
    data_load_state = st.text(
        "Loading collection data... if this is taking too long, try refreshing the page."
    )
    collection_data = get_random_collections(n=n_random)
    collection_data = add_collection_stats(collection_data)

    with st.expander("Random Collections, expand to view!"):
        cols = st.columns(2)
        for i, collection_data in enumerate(collection_data):
            c_num = i % 2
            if collection_data["creator_id"].endswith(".near"):
                creator = collection_data["creator_id"]
            else:
                creator = f"{collection_data['creator_id'][:8]}...{collection_data['creator_id'][-8:]}"

            try:
                r = requests.get(
                    f"https://ipfs.fleek.co/ipfs/{collection_data['media']}"
                )
                image = Image.open(io.BytesIO(r.content))
                cols[c_num].image(image)
            except:
                pass
            cols[c_num].subheader(f"{collection_data['collection']}")
            try:
                cols[c_num].caption(collection_data["description"])
            except:
                pass
            cols[c_num].write(
                f"""
    - **Creator:** {creator}
    - [**View on Paras**](https://paras.id/collection/{collection_data['collection_id']})
    {print_stats(collection_data)}
    -----
        """
            )
    data_load_state.text("")


st.header("Tour")
st.write(
    """
We've seen some random collections, let's look at the ones that attract the most visitors!
The top projects by volume are shown here:
"""
)
c1, c2 = st.columns([1, 3])
vol_type = c1.selectbox("Choose volume type:", ["Sales (NEAR)", "Number of sales"])
sales_vol = (
    alt.Chart(top_projects_df)
    .mark_bar(width=18)
    .transform_fold(fold=["Sales Count"], as_=["variable", "value"])
    .transform_window(
        rank="rank(value)", sort=[alt.SortField("value", order="descending")]
    )
    .transform_filter(alt.datum.rank <= 40)
    .encode(
        x=alt.X("NFT Collection", axis=alt.Axis(title=""), sort="-y"),
        y=alt.Y(
            "value:Q",
            title="Sales Count",
        ),
        color=alt.Color(
            "NFT Collection:N",
            sort=alt.EncodingSortField("value", op="max", order="descending"),
            scale=alt.Scale(
                scheme="tableau20",
            ),
        ),
        tooltip=[
            alt.Tooltip("NFT Collection", title="Collection Name"),
            alt.Tooltip("Total Volume (NEAR)", format=",.1f"),
            alt.Tooltip("Sales Count"),
            alt.Tooltip("Buyers"),
            alt.Tooltip("Sellers"),
        ],
    )
).interactive().properties(height=500)
near_vol = (
    alt.Chart(top_projects_df)
    .mark_bar(width=18)
    .transform_fold(
        fold=[
            "Total Volume (NEAR)",
        ],
        as_=["variable", "value"],
    )
    .transform_window(
        rank="rank(value)", sort=[alt.SortField("value", order="descending")]
    )
    .transform_filter(alt.datum.rank <= 40)
    .encode(
        x=alt.X("NFT Collection", axis=alt.Axis(title=""), sort="-y"),
        y=alt.Y("value:Q", title="Sales Volume (NEAR)"),
        color=alt.Color(
            "NFT Collection:N",
            sort=alt.EncodingSortField("value", op="max", order="descending"),
            scale=alt.Scale(
                scheme="tableau20",
            ),
        ),
        tooltip=[
            alt.Tooltip("NFT Collection", title="Collection Name"),
            alt.Tooltip("Total Volume (NEAR)", format=",.1f"),
            alt.Tooltip("Sales Count"),
            alt.Tooltip("Buyers"),
            alt.Tooltip("Sellers"),
        ],
    )
).interactive().properties(height=500)
if vol_type == "Sales (NEAR)":
    chart = near_vol
elif vol_type == "Number of sales":
    chart = sales_vol
st.altair_chart(chart, use_container_width=True)

st.write(
    """
Now we we can take a self-guided tour, taking a look at some collections in more detail! We can see the average, most expensive, and cheapest NFT sales each day, as well as the sales volume for the collection (in NEAR and number of transactions). The most popular collections from the last 7 days are here:
"""
)
st.write(past_week_df)
st.write(
"""
Enter the `NFT_CONTRACT_ID` for the collection you want to see in the text box below.
This will take some time to run, so results are cached for some of the more popular NFT collections:
- asac.near (Antisocial Ape Club)
- nearnautnft.near (NEARNauts)
- secretskelliessociety.near (Secret Skellies Society)

Use the checkbox to gather the latests results for one of these cached collections.
"""
)
c1, c2 = st.columns(2)
col_id = c1.text_input("Collection ID", "asac.near")
update_cache = c2.checkbox("Update data?")
try:
    r = requests.get(
        "https://api-v2-mainnet.paras.id/collections",
        params={"collection_id": col_id},
    )
    collection_data = r.json()["data"]["results"]
    collection_data = add_collection_stats(collection_data)[0]

    if collection_data["creator_id"].endswith(".near"):
        creator = collection_data["creator_id"]
    else:
        creator = f"{collection_data['creator_id'][:8]}...{collection_data['creator_id'][-8:]}"

    try:
        r = requests.get(f"https://ipfs.fleek.co/ipfs/{collection_data['media']}")
        image = Image.open(io.BytesIO(r.content))
        c2.image(image)
    except:
        pass
    c1.subheader(f"{collection_data['collection']}")
    try:
        c1.caption(collection_data["description"])
    except:
        pass
    c1.write(
        f"""
    - **Creator:** {creator}
    - [**View on Paras**](https://paras.id/collection/{collection_data['collection_id']})
    {print_stats(collection_data)}
    -----
    """
    )
except:
    c1.text(f"Error processing '{col_id}', try again with a different collection!")

query = f"""
--sql
with TX AS (
    SELECT
        blocK_timestamp,
        tx_hash,
        tx :receipt as receipt,
        tx :public_key as public_key,
        tx :signer_id as signer_id,
        tx :receiver_id as receiver_id
    FROM
        near.core.fact_transactions
),
JSON_PARSING AS (
    SELECT
        block_timestamp,
        tx_hash,
        public_key,
        signer_id,
        receiver_id,
        seq,
        key,
        path,
        index,
        replace(value :outcome :logs [0], '\\\\') as logs,
        -- remove // | convert variant | parse json
        check_json(logs) as checks
    FROM
        tx,
        table(flatten(input => receipt))
),
nft_tx_log AS (
    SELECT
        --PARSE_JSON(LOGS):PARAMS
        block_timestamp,
        tx_hash,
        public_key,
        signer_id,
        receiver_id,
        try_parse_json(logs) as parse_logs,
        parse_logs :type as type,
        parse_logs :params :buyer_id as buyer_id,
        parse_logs :params :owner_id as owner_id,
        parse_logs :params :is_offer as is_offer,
        parse_logs :params :is_auction as is_auction,
        parse_logs :params :nft_contract_id as nft_contract_id,
        parse_logs :params :token_id as token_id,
        parse_logs :params :ft_token_id as ft_token_id,
        parse_logs :params :price / pow(10, 24) as near
    FROM
        JSON_PARSING
    WHERE
        checks is null
        and logs is not null -- filter out json_parse 
        AND type is not null
)
SELECT
    date_trunc('day', block_timestamp :: date) as datetime,
    avg(NEAR) as average_sale_NEAR,
    sum(NEAR) as total_sale_NEAR,
    count(tx_hash) as total_tx,
    min(NEAR) as cheapest_NFT,
    max(NEAR) as most_expensive_NFT
FROM
    nft_tx_log
where
    type = 'resolve_purchase'
    and nft_contract_id = '{col_id}'
    and is_offer is NULL
    and is_auction is NULL
group by
    datetime
;
"""
data_load_state = st.text(
    "Loading data from Flipside... this will take several minutes unless the collection is cached"
)
sdk = ShroomDK(API_KEY)
# HACK: problem with loading data, so precomputing these here:
if col_id == "secretskelliessociety.near" and not update_cache:
    df = pd.read_csv("near/art/skellies.csv")
elif col_id == "nearnautnft.near" and not update_cache:
    df = pd.read_csv("near/art/nearnauts.csv")
elif col_id == "asac.near" and not update_cache:
    df = pd.read_csv("near/art/asac.csv")
else:
    try:
        df = get_flipside_data(query, cached=True)
    except errors.UserError:
        df = get_flipside_data(query, cached=False)
data_load_state.text("")


df = df.rename(
    columns={
        "AVERAGE_SALE_NEAR": "Average Sale",
        "CHEAPEST_NFT": "Cheapest NFT",
        "MOST_EXPENSIVE_NFT": "Most Expensive NFT",
        "TOTAL_SALE_NEAR": "Total Sale Volume",
        "TOTAL_TX": "Number of Sales",
    }
)
sale_df = df[
    [
        "DATETIME",
        "Average Sale",
        "Cheapest NFT",
        "Most Expensive NFT",
    ]
].melt(id_vars=["DATETIME"])

c1, c2 = st.columns(2)
chart = alt_line_chart(sale_df).properties(height=500)
c1.altair_chart(chart, use_container_width=True)

chart1 = (
    alt.Chart(
        df,
        title=f"Sale Volume: {collection_data['collection']} ({col_id})",
    )
    .mark_bar()
    .encode(
        x=alt.X(
            "yearmonthdate(DATETIME):T",
            axis=alt.Axis(title=""),
        ),
        y=alt.Y("Number of Sales"),
        tooltip=[
            alt.Tooltip("yearmonthdate(DATETIME)", title="Date"),
            alt.Tooltip("Number of Sales", type="quantitative", format=","),
            alt.Tooltip("Total Sale Volume", type="quantitative", format=",.2f"),
        ],
    )
    .interactive()
    .properties(height=500)
)

chart2 = (
    alt.Chart(
        df,
    )
    .mark_line(color="red")
    .encode(
        x=alt.X(
            "yearmonthdate(DATETIME):T",
            axis=alt.Axis(title=""),
        ),
        y=alt.Y("Total Sale Volume", title="Sale Volume (NEAR)"),
        tooltip=[
            alt.Tooltip("yearmonthdate(DATETIME)", title="Date"),
            alt.Tooltip("Number of Sales", type="quantitative", format=","),
            alt.Tooltip("Total Sale Volume", type="quantitative", format=",.2f"),
        ],
    )
    .interactive()
    .properties(height=500)
)
c2.altair_chart(
    alt.layer(chart1, chart2).resolve_scale(y="independent"), use_container_width=True
)
