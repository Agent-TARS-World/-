#!/usr/bin/env python3
"""Batch-generate Agent-World demo videos for multiple conversations."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from generate_video import generate_video_for

DEMOS = [
    # ── 1. Flight Refund ──────────────────────────────────────────────
    {
        "title": "Flight Refund Evaluation",
        "file": "demo_flight.mp4",
        "steps": [
            ("user", "I booked flight 1451 with airline W9\non 2025-07-16, account john_smith_123,\nticket price $320.\nPlease check auto-refund eligibility\nand return JSON."),
            ("think", "Need to get flight status, airline info,\nand user payment method.\n1. get_flight_status - check cancellation\n2. get_airline_by_iata - check if active\n3. get_user_by_id - get payment method"),
            ("fn", 'get_flight_status(\n  flight_number="1451",\n  date="2025-07-16"\n)'),
            ("tool", "{'flight_number': '1451',\n 'status': 'Cancelled',\n 'estimated_departure': '07:00',\n 'estimated_arrival': '21:30'}"),
            ("fn", 'get_airline_by_iata(iata_code="W9")'),
            ("tool", "{'Name': 'Abelag Aviation',\n 'IATA': 'W9',\n 'Country': 'Belgium',\n 'Active': 'N'}"),
            ("fn", 'get_user_by_id(\n  user_id="john_smith_123"\n)'),
            ("tool", "{'name': 'John Smith',\n 'payment_methods': [{\n   'type': 'credit_card',\n   'last4': '4567'}]}"),
            ("think", "Flight cancelled -> 100% refund = $320\nAirline Active='N' -> High Risk\nSingle payment method: credit card last4=4567"),
            ("answer", '{\n  "user_name": "John Smith",\n  "airline_name": "Abelag Aviation",\n  "refund_usd": 320,\n  "refund_to_payment_last4": "4567",\n  "risk_level": "High Risk"\n}'),
        ],
    },
    # ── 2. Ecomm Return ───────────────────────────────────────────────
    {
        "title": "Ecomm Return Processing",
        "file": "demo_ecomm.mp4",
        "steps": [
            ("user", "Hey! I need to return a few things.\nMy name is Anya Sanchez,\nzip code is 43171."),
            ("think", "First authenticate the user via name + zip.\nThen find delivered orders eligible for return.\nCheck payment method for refund."),
            ("fn", 'find_user_id_by_name_zip(\n  first_name="Anya",\n  last_name="Sanchez",\n  zip="43171"\n)'),
            ("tool", '"anya_sanchez_9707"'),
            ("fn", 'get_user_details(\n  user_id="anya_sanchez_9707"\n)'),
            ("tool", '{"name": "Anya Sanchez",\n "orders": ["#W5402785",\n  "#W2136962", "#W4442043",\n  "#W6002958"],\n "payment": "paypal_1191071"}'),
            ("think", "4 orders found. Checking status:\n#W5402785 -> pending\n#W2136962 -> processed\n#W4442043 -> delivered\n#W6002958 -> pending\nOnly #W4442043 eligible for return."),
            ("fn", 'return_delivered_order_items(\n  order_id="#W4442043",\n  items=["6697922351",\n   "7758198585","3187628796"],\n  payment="paypal_1191071"\n)'),
            ("tool", '{"status": "return requested",\n "return_items":\n  ["3187628796",\n   "6697922351",\n   "7758198585"]}'),
            ("answer", "Return request processed!\n\nOrder #W4442043 -> return requested\nItems: Helmet, Bicycle, Smartphone\nRefund to PayPal (5-7 business days)"),
        ],
    },
    # ── 3. Notion Consistency ─────────────────────────────────────────
    {
        "title": "Note Consistency Check",
        "file": "demo_notion.mp4",
        "steps": [
            ("user", "Search for a same-name page using the\nfirst title in the page list.\nCheck nested to-do vs plain paragraph\nfor consistency.\nRules: missing=50, incomplete=30, mismatch=20\nTotal>=50 -> High Risk"),
            ("fn", "get_example_page()"),
            ("tool", '{"properties":{\n  "Name":{"title":[{\n    "plain_text":"Tuscan kale"}]},\n  "Price":{"number":2.5}}}'),
            ("fn", 'query_example_database(\n  property_name="Name",\n  value="Tuscan kale"\n)'),
            ("tool", "[]"),
            ("think", "No same-name page found -> missing +50\nContinue checking nested to-do and paragraph"),
            ("fn", "get_example_block_todo_nested()"),
            ("tool", '{"has_children": true,\n "children": [{"type": "to_do",\n   "to_do":{"checked": false}}]}'),
            ("fn", "get_example_block_paragraph()"),
            ("tool", '{"has_children": false,\n "paragraph": {"text": []}}'),
            ("think", "checked=false -> +30\nhas_children mismatch -> +20\nTotal = 50+30+20 = 100 >= 50\nConclusion: High Risk"),
            ("answer", '{\n  "page_title": "Tuscan kale",\n  "db_same_name_count": 0,\n  "risk_score": 100,\n  "risk_level": "High Risk"\n}'),
        ],
    },
    # ── 4. Slack Compliance ───────────────────────────────────────────
    {
        "title": "Compliance Inspection",
        "file": "demo_slack.mp4",
        "steps": [
            ("user", "Analyze reported message at timestamp\n1512104434.000490 correlated with user\nU123ABC456. Check login status and\ncontacts. Output triage level and\nticket comments."),
            ("fn", 'get_message_by_ts(\n  ts="1512104434.000490"\n)'),
            ("tool", '{"user": "U222BBB222",\n "text": "What, you want to\n  smell my shoes better?"}'),
            ("fn", 'get_user_by_id("U222BBB222")'),
            ("tool", '{"status": "not_found"}'),
            ("fn", 'filter_message_csv_by_user(\n  user_id="U123ABC456"\n)'),
            ("tool", '{"text": "I find you punny\n  and would like to smell\n  your nose letter",\n "ts": "1512085950.000216"}'),
            ("fn", 'get_login_status("W012A3CDE")'),
            ("tool", '{"is_logged_in": true,\n "last_login":\n  "2025-06-28T12:00:00Z"}'),
            ("think", "Sender not found (possibly deleted)\nJaccard similarity -> 0.18\nTime diff 18484 seconds\nContact already exists -> no add needed\n-> Triage level: ignore"),
            ("answer", '{\n  "report_sender_id": "U222BBB222",\n  "similarity_score": 0.18,\n  "time_diff_seconds": 18484,\n  "need_add_contact": false,\n  "triage_level": "ignore"\n}'),
        ],
    },
    # ── 5. Population Data ────────────────────────────────────────────
    {
        "title": "City Influence Index",
        "file": "demo_population.mp4",
        "steps": [
            ("user", "Get top 10 cities by population + Karachi.\nCompute influence index S=ln(pop/40).\nMultiply Karachi by 1+growthRate.\nSelect the highest and convert to\nlog magnitude."),
            ("fn", "list_top_cities_by_population(\n  limit=10\n)"),
            ("tool", "[{Tokyo: 37194104},\n {Delhi: 32941308},\n {Shanghai: 29210808},\n {Dhaka: 23209616},\n {Sao Paulo: 22619736}, ...]"),
            ("fn", 'get_city_population(\n  city="Karachi",\n  country="Pakistan"\n)'),
            ("tool", '{"Pop2023": 17236230,\n "growthRate": 0.0235}'),
            ("fn", 'get_city_population_percentage(\n  city="Tokyo"\n)'),
            ("tool", "1.798%"),
            ("think", "Tokyo S ~ 13.74 (highest)\nDelhi S ~ 13.62\nKarachi S ~ 12.97 x 1.0235 ~ 13.28\n-> Tokyo wins\nM = log2(S) / log2(10)"),
            ("fn", "get_logarithms_for_value(x=10)"),
            ("tool", '{"log2": 3.321928,\n "ln": 2.302585}'),
            ("answer", '{\n  "winner_city": "Tokyo",\n  "winner_country": "Japan",\n  "score_S": 13.7423,\n  "magnitude_M": 1.1384\n}'),
        ],
    },
    # ── 6. Telecom Support ────────────────────────────────────────────
    {
        "title": "Mobile Network Diagnosis",
        "file": "demo_telecom.mp4",
        "steps": [
            ("user", "My mobile data isn't working properly.\nSometimes it stops, and other times\nit's really slow.\nMy phone number is 555-123-2002."),
            ("fn", 'get_customer_by_phone(\n  phone="555-123-2002"\n)'),
            ("tool", '{"customer_id": "C1001",\n "name": "John Smith",\n "line_ids":\n  ["L1001","L1002","L1003"]}'),
            ("fn", 'get_details_by_id(id="L1002")'),
            ("tool", '{"phone": "555-123-2002",\n "status": "Active",\n "plan_id": "P1002",\n "data_used_gb": 8.7}'),
            ("fn", 'get_details_by_id(id="P1002")'),
            ("tool", '{"name": "Premium Plan",\n "data_limit_gb": 15.0,\n "price_per_month": 65.0}'),
            ("think", "Data usage 8.7 / 15 GB within limit\nLine status normal\nChecking network mode -> user on 2G only\nSwitching to 4G/5G -> speed restored"),
            ("answer", "Issue resolved!\n\nRoot cause: Network mode set to 2G\n-> Switched to 4G/5G preferred\n-> Airplane mode OFF, data ON\n-> Speed test: 275 Mbps (Excellent)"),
        ],
    },
    # ── 7. Twitter Engagement ─────────────────────────────────────────
    {
        "title": "Engagement Value Audit",
        "file": "demo_twitter.mp4",
        "steps": [
            ("user", "Log in as TwitterDev and perform an\nengagement value audit:\n1. Verify profile consistency\n2. Find highest-influence in following\n3. Check tweet_id=2 comment ratio\n   from followed users."),
            ("fn", 'get_user_by_username(\n  username="TwitterDev"\n)'),
            ("tool", '{"id": "2244994945",\n "name": "X Dev",\n "username": "TwitterDev",\n "followers_count": 513958,\n "friends_count": 2039}'),
            ("fn", "list_following()"),
            ("tool", '[{"username": "TwitterDev",\n  "id": "2244994945",\n  "name": "X Dev"}]'),
            ("fn", 'get_comments_for_tweet(\n  tweet_id="2"\n)'),
            ("tool", '[{"User":{"account":"user1"},\n  "comment":"comment",\n  "TweetId": 2}]'),
            ("think", "Profile consistent: username / id / name /\nprotected / created_at all match -> true\nFollowing list: only self\nInfluence = 513958/2039 ~ 252.06\nCommenter user1 not in following list"),
            ("answer", '{\n  "profile_consistency": true,\n  "top_influence_user":\n    "TwitterDev",\n  "top_influence_score": 252.06,\n  "tweet2_comment_ratio": 0,\n  "has_following_comment": false\n}'),
        ],
    },
    # ── 8. GitHub Admin ───────────────────────────────────────────────
    {
        "title": "Repository Management",
        "file": "demo_github.mp4",
        "steps": [
            ("user", "I've been promoted! Please:\n1. Update username -> adryzzVP\n2. Email -> adryzzVP@...github.com\n3. Role -> owner\n4. Make all repos private\n5. Create repo VPTeamFormation"),
            ("fn", 'getUserByUsername(\n  username="adryzz"\n)'),
            ("tool", '{"id": 1166,\n "username": "adryzz",\n "role": "collaborator"}'),
            ("fn", 'updateUser(\n  id=1166,\n  username="adryzzVP",\n  email="adryzzVP@...github.com",\n  role="owner"\n)'),
            ("tool", '{"id": 1166,\n "username": "adryzzVP",\n "role": "owner"}'),
            ("fn", "getRepositories(owner_id=1166)"),
            ("tool", '[{"id": 160,\n  "name": "Ibralogue",\n  "is_private": false}]'),
            ("fn", 'updateRepository(\n  id=160, is_private=true\n)'),
            ("tool", '{"name": "Ibralogue",\n "is_private": true}'),
            ("fn", 'createRepository(\n  name="VPTeamFormation",\n  is_private=true,\n  default_branch="team1"\n)'),
            ("tool", '{"id": 161,\n "name": "VPTeamFormation",\n "is_private": true,\n "default_branch": "team1"}'),
            ("answer", "All tasks completed!\n1. Username -> adryzzVP, role -> owner\n2. Ibralogue -> private\n3. VPTeamFormation created (team1)"),
        ],
    },
    # ── 9. Document Governance ────────────────────────────────────────
    {
        "title": "Database Governance",
        "file": "demo_document.mp4",
        "steps": [
            ("user", "Travel database governance check:\nVerify user e79a0b74's name.\nCheck database c3f0603a status property\nagainst tag category standards."),
            ("fn", 'get_user_by_id(\n  "e79a0b74-3aba-..."\n)'),
            ("tool", '{"name": "Avocado Lovelace",\n "email": "avocado@example.org"}'),
            ("fn", 'get_database_by_id(\n  "c3f0603a-3cd3-..."\n)'),
            ("tool", '{"title": "Travel Itineraries",\n "properties": {\n  "Status": {"select": {\n    "options": ["Planned",\n     "Booked","Completed",\n     "Cancelled"]}}}}'),
            ("fn", "list_tag_categories()"),
            ("tool", '["Status", "Department",\n "Quarter", "Travel Status",\n "Category", "General Tags"]'),
            ("fn", "list_databases()"),
            ("tool", '[Onboarding Tasks: Status\n Quarterly Reviews: Quarter\n Travel Itineraries: Status\n SOP Library: Category]'),
            ("think", "Status property matches tag category 'Status'\n2/2 status-type databases fully match -> 100%\nTravel DB compliant, recommend keeping 'Status'"),
            ("answer", '{\n  "report_owner_name":\n    "Avocado Lovelace",\n  "travel_db_status_property":\n    "Status",\n  "recommended_category":\n    "Status",\n  "exact_match_ratio": 100.0\n}'),
        ],
    },
]

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    total = len(DEMOS)
    for i, demo in enumerate(DEMOS, 1):
        out = os.path.join(base, demo["file"])
        print(f"\n{'='*60}")
        print(f"[{i}/{total}] {demo['title']}  →  {demo['file']}")
        print(f"{'='*60}")
        generate_video_for(demo["title"], demo["steps"], out)
    print(f"\n✅ All {total} videos generated!")
