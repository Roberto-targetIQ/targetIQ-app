import streamlit as st
import requests
import pandas as pd

# 🔑 Replace with your Apollo API key
APOLLO_API_KEY = "gFBWke7MH7PujP4Jd3Tr1A"

TARGET_TITLES = [
    "procurement", "purchasing", "sourcing",
    "materials", "engineering", "r&d",
    "product", "supply chain", "operations"
]

def search_companies(product):
    url = "https://api.apollo.io/v1/mixed_companies/search"
    payload = {"api_key": APOLLO_API_KEY, "q_keywords": product}
    res = requests.post(url, json=payload)
    return res.json().get("organizations", [])

def find_contacts(domain):
    url = "https://api.apollo.io/v1/people/search"
    payload = {"api_key": APOLLO_API_KEY, "q_organization_domains": [domain]}
    res = requests.post(url, json=payload)
    return res.json().get("people", [])

def score_contact(title):
    score = 0
    title = title.lower()
    for keyword in TARGET_TITLES:
        if keyword in title:
            score += 1
    if any(x in title for x in ["director", "vp", "head", "chief"]):
        score += 2
    return score

st.set_page_config(page_title="TargetIQ", layout="wide")
st.title("🎯 TargetIQ")

product = st.text_input("What product/service are you selling?")

if st.button("Find Targets") and product:
    st.write("🔍 Searching...")
    companies = search_companies(product)
    all_contacts = []

    for company in companies[:5]:
        st.subheader(company["name"])
        contacts = find_contacts(company.get("website_url"))
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
            st.write("No strong contacts found.")

    if all_contacts:
        df = pd.DataFrame(all_contacts)
        st.download_button("Download CSV", df.to_csv(index=False), "targetiq_leads.csv")
