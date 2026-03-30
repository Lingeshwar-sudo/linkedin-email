import streamlit as st
import requests
import re
import pandas as pd
import time
import urllib.parse
import base64

HUNTER_API_KEY = "72ba12abe4c6ee2bfc279d9233d38bbba389202b"

# ---------- Background ----------
def add_bg_from_local():
    with open("bg_photo.jpeg", "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}

        h1, h2, h3, h4, h5, h6, p, label {{
            color: white !important;
        }}

        .card {{
            background-color: rgba(0, 0, 0, 0.65);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }}

        .email-text {{
            font-size: 18px;
            font-weight: bold;
            color: #00FFCC;
        }}

        .name-text {{
            color: white;
            font-size: 16px;
        }}

        .role-text {{
            color: #FFD700;
            font-size: 15px;
        }}

        .gmail-btn {{
            background-color: #00C9A7;
            color: white;
            padding: 8px 15px;
            border-radius: 8px;
            text-decoration: none;
        }}

        .stButton>button {{
            background-color: #00C9A7;
            color: white;
            border-radius: 10px;
            height: 2.5em;
            width: 200px;
            font-size: 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local()

# ---------- Functions ----------

def get_company_domain(linkedin_url):
    try:
        name = re.search(r'company/([^/]+)', linkedin_url).group(1)
        name = name.replace('-', '')
        return name + ".com"
    except:
        return None


def find_emails(domain):
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY
    }

    response = requests.get(url, params=params)
    results = []

    if response.status_code == 200:
        data = response.json()["data"]["emails"]

        for email in data:
            role = email.get("position", "")
            email_value = email.get("value", "")
            name = (email.get("first_name", "") + " " + email.get("last_name", "")).strip()

            if not role:
                if "ceo" in email_value:
                    role = "CEO"
                elif "sales" in email_value:
                    role = "Sales"
                elif "hr" in email_value:
                    role = "HR"
                else:
                    role = "Not Available"

            results.append({
                "email": email_value,
                "name": name,
                "role": role
            })

    return results


# ---------- Email Template ----------

def generate_email_template(company, name=""):
    subject = f"Exploring Opportunities to Support {company}'s Operational Efficiency"

    body = f"""
Hi {name if name else ''},

I hope you’re doing well.

I came across your profile and was impressed by your experience in driving operational efficiency and optimizing business processes within your organization.

Your approach to improving workflows and building scalable systems aligns closely with the kind of challenges we help solve.

I’m reaching out from IcebergTech. We offer end-to-end IT services and solutions focused on:

• Custom software development
• Workflow automation
• Data-driven decision support
• Mobile and web application development
• System integration and process optimization

Our solutions are designed to help organizations streamline operations, improve efficiency, and build scalable systems for long-term growth.

I would be glad to connect and understand your current requirements to explore how we can support your initiatives. Please let me know a convenient time to connect.

Looking forward to your response.

Best regards,
Lingesh
IcebergTech
+91XXXXXXXXXX
"""
    return subject, body


# ---------- UI ----------

st.title("LinkedIn Company Email Finder")

url = st.text_input("Enter LinkedIn Company URL")

if st.button("Find Emails"):
    if url:
        domain = get_company_domain(url)

        if domain:
            st.success(f"Company Domain: {domain}")
            people = find_emails(domain)

            if people:
                st.subheader("Contacts Found")

                for person in people:
                    email = person["email"]
                    name = person["name"]
                    role = person["role"]

                    subject, body = generate_email_template(domain, name)

                    subject_encoded = urllib.parse.quote(subject)
                    body_encoded = urllib.parse.quote(body)

                    gmail_link = f"https://mail.google.com/mail/u/0/?fs=1&tf=cm&source=mailto&to={email}&su={subject_encoded}&body={body_encoded}"

                    st.markdown(f"""
                    <div class="card">
                        <div class="email-text">{email}</div>
                        <div class="name-text">Name: {name}</div>
                        <div class="role-text">Role: {role}</div>
                        <br>
                        <a class="gmail-btn" href="{gmail_link}" target="_blank">Send Email via Gmail</a>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.error("No emails found.")
        else:
            st.error("Invalid LinkedIn URL")


# ---------- CSV Upload ----------

st.subheader("Upload CSV")
uploaded_file = st.file_uploader("Upload CSV with LinkedIn URLs", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    results = []

    for index, row in df.iterrows():
        domain = get_company_domain(row["linkedin_url"])
        if domain:
            people = find_emails(domain)
            for person in people:
                results.append({
                    "company": row["company_name"],
                    "domain": domain,
                    "email": person["email"],
                    "name": person["name"],
                    "role": person["role"]
                })
        time.sleep(1)

    result_df = pd.DataFrame(results)
    st.write(result_df)

    result_df.to_csv("output.csv", index=False)
