import streamlit as st
import requests
import pandas as pd

# 🔑 Replace this with your actual Apollo.io API key
APOLLO_API_KEY = "gFBWke7MH7PujP4Jd3Tr1A"

# Titles we want to prioritize
TARGET_TITLES = [
    "procurement", "purchasing", "sourcing",
    "materials", "engineering", "r&d",
    "product", "supply chain", "operations"
]

# Function to search companies
def search_companies(product):
    url = "https://api.apollo.io/v1/mixed_companies/search"
    payload = {"api_key": APOLLO_API_KEY, "q_keywords": product}
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code != 200:
            st.error(f"Company search error: {res.status_code}")
            st.write(res.text)
            return []
        return res.json().get("organizations", [])
    except Exception as e:
        st.error(f"Company search failed: {e}")
        return []

# Function to find contacts at a company
def find_contacts(domain):
    if not domain:
        return []
    url = "https://api.apollo.io/v1/people/search"
    payload = {"api_key": APOLLO_API_KEY, "q_organization_domains": [domain]}
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code != 200:
            st.warning(f"Contact search error for {domain}: {res.status_code}")
            return []
        return res.json().get("people", [])
    except Exception as e:
        st.warning(f"Contact search failed for {domain}: {e}")
        return []

# Function to score contacts
def score_contact(title):
    score = 0
    title = title.lower()
    for keyword in TARGET_TITLES:
        if keyword in title:
            score += 1
    if any(x in title for x in ["director", "vp", "head", "chief"]):
        score += 2
    return score

# Streamlit app layout
st.set_page_config(page_title="TargetIQ", layout="wide")
st.title("🎯 TargetIQ")

product = st.text_input("What product/service are you selling?")

if st.button("Find Targets") and product:
    all_contacts = []

    with st.spinner("Searching for companies..."):
        companies = search_companies(product)

    if not companies:
        st.warning("No companies found. Check your API key and product keywords.")
    else:
        for company in companies[:5]:  # limit to 5 companies for speed
            st.subheader(company.get("name", "Unnamed Company"))
            domain = company.get("website_url") or company.get("domain")
            with st.spinner(f"Searching contacts for {company.get('name')}..."):
                contacts = find_contacts(domain)
            scored_contacts = []
            for c in contacts:
                title = c.get("title", "")
                if title:
                    score = score_contact(title)
                    if score > 0:
                        scored_contacts.append({
                            "name": c.get("name"),
                            "title": title,
                            "email": c.get("email"),
                            "score": score
                        })

            best_contacts = sorted(scored_contacts, key=lambda x: x["score"], reverse=True)[:3]

            if best_contacts:
                for c in best_contacts:
                    st.write(f"{c['name']} | {c['title']} | {c['email']} | Score: {c['score']}")
                    all_contacts.append(c)
            else:
                st.write("No strong contacts found for this company.")

        if all_contacts:
            df = pd.DataFrame(all_contacts)
            st.download_button("Download CSV", df.to_csv(index=False), "targetiq_leads.csv")
