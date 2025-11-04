import requests
import streamlit as st
from urllib.parse import quote

st.set_page_config(
    page_title="Art Explorer • wang xinru",
    page_icon="🖼️",
    layout="wide"
)

st.title("Art Explorer • wang xinru")
st.caption("Search artworks from The Met Museum (no API key required)")

@st.cache_data(show_spinner=False, ttl=3600)
def met_search_object_ids(query: str):
    if not query:
        return []
    url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {"hasImages": "true", "q": query}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data.get("objectIDs", []) or []

@st.cache_data(show_spinner=False, ttl=3600)
def met_get_object(object_id: int):
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()

def info_row(label, value):
    if value in (None, "", [], {}):
        return
    if isinstance(value, list):
        value = ", ".join([str(v) for v in value if v])
    st.markdown(f"**{label}**: {value}")

with st.sidebar:
    st.header("Search")
    query = st.text_input("Keyword", placeholder="e.g., Van Gogh, birds, porcelain, Ming...")
    page_size = st.selectbox("Results per page", [9, 12, 15, 18, 24], index=2)
    st.divider()
    st.markdown(
        "Data source: **The Met Museum Collection API**. "
        "Images and text belong to their respective rights holders."
    )

if query:
    with st.spinner("Searching…"):
        ids = met_search_object_ids(query)

    if not ids:
        st.info("No results found. Try another keyword.")
    else:
        page = st.session_state.get("page", 1)
        col1, col2, col3 = st.columns([1, 2, 1])
        total = len(ids)
        total_pages = (total + page_size - 1) // page_size

        with col1:
            if st.button("◀ Prev", use_container_width=True, disabled=page <= 1):
                page = max(1, page - 1)
        with col3:
            if st.button("Next ▶", use_container_width=True, disabled=page >= total_pages):
                page = min(total_pages, page + 1)
        st.session_state["page"] = page

        start = (page - 1) * page_size
        end = min(start + page_size, total)
        st.write(f"Showing **{start+1}–{end}** of **{total}** results")

        grid_cols = st.columns(3)
        for i, obj_id in enumerate(ids[start:end]):
            col = grid_cols[i % 3]
            with col:
                try:
                    data = met_get_object(obj_id)
                except Exception:
                    continue

                img_url = data.get("primaryImageSmall") or data.get("primaryImage")
                title = data.get("title") or "Untitled"
                artist = data.get("artistDisplayName") or ""
                date = data.get("objectDate") or ""
                dept = data.get("department") or ""

                with st.container(border=True):
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    st.markdown(f"**{title}**")
                    st.caption(" · ".join([x for x in [artist, date, dept] if x]))
                    with st.expander("Details"):
                        info_row("Artist", data.get("artistDisplayName"))
                        info_row("Artist Bio", data.get("artistDisplayBio"))
                        info_row("Title", data.get("title"))
                        info_row("Object Name", data.get("objectName"))
                        info_row("Department", data.get("department"))
                        info_row("Object Date", data.get("objectDate"))
                        info_row("Object Begin–End Date", f"{data.get('objectBeginDate')} – {data.get('objectEndDate')}")
                        info_row("Medium", data.get("medium"))
                        info_row("Measurements", data.get("dimensions"))
                        info_row("Culture/Period", ", ".join([x for x in [data.get('culture'), data.get('period')] if x]))
                        info_row("Geography", ", ".join([x for x in [data.get('city'), data.get('state'), data.get('country'), data.get('region')] if x]))
                        info_row("Accession Number", data.get("accessionNumber"))
                        info_row("Accession Year", data.get("accessionYear"))
                        info_row("Credit Line", data.get("creditLine"))
                        info_row("Tags", [t.get("term") for t in (data.get("tags") or [])])
else:
    st.info("Enter a keyword in the sidebar to start searching.")
