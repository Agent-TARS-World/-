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
        "l1": "Travel & Transportation",
        "l2": "Booking & Hospitality",
        "l3": "Flight and Stay Search Server",
        "steps": [
            ("user",
             "I booked flight **1451** with airline IATA code **W9**\n"
             "on **2025-07-16**, my account is **john_smith_123**.\n"
             "Ticket price is **$320**.\n"
             "Refund rules:\n"
             "- Cancelled -> 100% refund\n"
             "- Not cancelled but arrival > departure\n"
             "  by more than 10 hours -> 50% refund\n"
             "- Otherwise -> $0\n"
             "If airline is inactive -> mark as high risk.\n"
             "Refund to the only credit card on file.\n"
             "Return JSON with user_name, airline_name,\n"
             "refund_usd, refund_to_payment_last4, risk_level."),
            ("think",
             "Need to gather three pieces of information:\n"
             "1. get_flight_status -> check if cancelled\n"
             "2. get_airline_by_iata -> check if airline is active\n"
             "3. get_user_by_id -> get payment method\n"
             "These can be called in sequence since\n"
             "each provides independent info."),
            ("fn",
             'get_flight_status(\n'
             '  flight_number="1451",\n'
             '  date="2025-07-16"\n'
             ')'),
            ("tool",
             "{'flight_number': '1451',\n"
             " 'date': '2025-07-16',\n"
             " 'status': 'Cancelled',\n"
             " 'estimated_departure': '07:00:00',\n"
             " 'estimated_arrival': '21:30:00'}"),
            ("fn",
             'get_airline_by_iata(\n'
             '  iata_code="W9"\n'
             ')'),
            ("tool",
             "{'Airline_ID': '15',\n"
             " 'Name': 'Abelag Aviation',\n"
             " 'Alias': None,\n"
             " 'IATA': 'W9',\n"
             " 'ICAO': 'AAB',\n"
             " 'Callsign': 'ABG',\n"
             " 'Country': 'Belgium',\n"
             " 'Active': 'N'}"),
            ("fn",
             'get_user_by_id(\n'
             '  user_id="john_smith_123"\n'
             ')'),
            ("tool",
             "{'user_id': 'john_smith_123',\n"
             " 'name': 'John Smith',\n"
             " 'email': 'john.smith@example.com',\n"
             " 'payment_methods': [{\n"
             "   'payment_id': 'credit_card_1234567',\n"
             "   'type': 'credit_card',\n"
             "   'last4': '4567'}]}"),
            ("think",
             "Flight status = Cancelled\n"
             "-> Rule: cancelled = 100% refund = $320\n\n"
             "Airline Active = 'N' (inactive)\n"
             "-> Risk level: high risk\n\n"
             "Payment methods: only 1 credit card\n"
             "-> last4 = '4567' (valid, single method)\n\n"
             "All conditions met, generating result."),
            ("answer",
             '{\n'
             '  "user_name": "John Smith",\n'
             '  "airline_name": "Abelag Aviation",\n'
             '  "refund_usd": 320,\n'
             '  "refund_to_payment_last4": "4567",\n'
             '  "risk_level": "High Risk"\n'
             '}'),
        ],
    },
    # ── 2. Ecomm Return ───────────────────────────────────────────────
    {
        "title": "Ecomm Return Processing",
        "file": "demo_ecomm.mp4",
        "l1": "Search & Information Retrieval",
        "l2": "API Gateway & Aggregation",
        "l3": "Ecomm MCP Server",
        "steps": [
            ("user",
             "Hey! I need to return a few things\n"
             "I bought recently.\n"
             "My name is Anya Sanchez\n"
             "and my zip code is 43171."),
            ("think",
             "Need to authenticate the user first.\n"
             "Using name + zip code to find user ID.\n"
             "Then check orders for delivered items\n"
             "eligible for return."),
            ("fn",
             'find_user_id_by_name_zip(\n'
             '  first_name="Anya",\n'
             '  last_name="Sanchez",\n'
             '  zip="43171"\n'
             ')'),
            ("tool",
             '"anya_sanchez_9707"'),
            ("fn",
             'get_user_details(\n'
             '  user_id="anya_sanchez_9707"\n'
             ')'),
            ("tool",
             '{"user_id": "anya_sanchez_9707",\n'
             ' "name": {"first_name": "Anya",\n'
             '  "last_name": "Sanchez"},\n'
             ' "address": {"city": "Columbus",\n'
             '  "state": "OH", "zip": "43171"},\n'
             ' "payment_methods": {\n'
             '  "paypal_1191071": {\n'
             '   "source": "paypal"}},\n'
             ' "orders": ["#W5402785",\n'
             '  "#W2136962", "#W4442043",\n'
             '  "#W6002958"]}'),
            ("think",
             "4 orders found. Checking each status:\n"
             "#W5402785 -> pending (not eligible)\n"
             "#W2136962 -> processed (not eligible)\n"
             "#W4442043 -> delivered (eligible!)\n"
             "#W6002958 -> pending (not eligible)\n\n"
             "Order #W4442043 items:\n"
             "- Backpack ($212.79)\n"
             "- Cycling Helmet ($194.47)\n"
             "- Smartphone ($1205.66)\n"
             "- Bicycle ($1917.21)"),
            ("user",
             "I want to return the cycling helmet,\n"
             "the bicycle, and the smartphone.\n"
             "Refunding to my PayPal is fine."),
            ("fn",
             'return_delivered_order_items(\n'
             '  order_id="#W4442043",\n'
             '  item_ids=["6697922351",\n'
             '    "7758198585", "3187628796"],\n'
             '  payment_method_id=\n'
             '    "paypal_1191071"\n'
             ')'),
            ("tool",
             '{"order_id": "#W4442043",\n'
             ' "status": "return requested",\n'
             ' "return_items": [\n'
             '  "3187628796",\n'
             '  "6697922351",\n'
             '  "7758198585"],\n'
             ' "return_payment_method_id":\n'
             '  "paypal_1191071"}'),
            ("answer",
             "Return request processed successfully!\n\n"
             "Order #W4442043 -> return requested\n"
             "Items: Cycling Helmet, Bicycle,\n"
             "  Smartphone\n"
             "Refund to PayPal (paypal_1191071)\n"
             "Processing time: 5-7 business days"),
        ],
    },
    # ── 3. Notion Consistency ─────────────────────────────────────────
    {
        "title": "Note Consistency Check",
        "file": "demo_notion.mp4",
        "l1": "Document & Design",
        "l2": "Office & Text Processing",
        "l3": "Notion MCP Server",
        "steps": [
            ("user",
             "Check the first page title from the\n"
             "page list, search for same-name pages\n"
             "in the database.\n"
             "Then compare nested to-do block vs\n"
             "plain paragraph block for consistency.\n\n"
             "Rules:\n"
             "- Missing page = 50 pts\n"
             "- Unchecked to-do = 30 pts\n"
             "- Children mismatch = 20 pts\n"
             "Total >= 50 -> High Risk"),
            ("fn", "get_example_page()"),
            ("tool",
             "{'object': 'page',\n"
             " 'id': '59833787-2cf9-4fdf-...',\n"
             " 'properties': {\n"
             "  'Name': {'type': 'title',\n"
             "   'title': [{'plain_text':\n"
             "    'Tuscan kale'}]},\n"
             "  'Price': {'number': 2.5},\n"
             "  'Food group': {'select':\n"
             "   {'name': 'Vegetable'}},\n"
             "  'In stock': {'checkbox': True}}}"),
            ("fn",
             'query_example_database(\n'
             '  property_name="Name",\n'
             '  value="Tuscan kale"\n'
             ')'),
            ("tool", "[]"),
            ("think",
             "No same-name page found in database\n"
             "-> Missing: +50 points\n\n"
             "Now checking nested to-do block\n"
             "and plain paragraph block."),
            ("fn", "get_example_block_todo_nested()"),
            ("tool",
             "{'object': 'block',\n"
             " 'id': '380c78c0-e0f5-...',\n"
             " 'type': 'paragraph',\n"
             " 'has_children': True,\n"
             " 'paragraph': {'children': [{\n"
             "   'type': 'to_do',\n"
             "   'to_do': {'checked': False}\n"
             " }]}}"),
            ("fn", "get_example_block_paragraph()"),
            ("tool",
             "{'object': 'block',\n"
             " 'id': '380c78c0-e0f5-...',\n"
             " 'type': 'paragraph',\n"
             " 'has_children': False,\n"
             " 'paragraph': {'text': []}}"),
            ("think",
             "to_do.checked = false\n"
             "-> Unchecked to-do: +30 points\n\n"
             "Nested block has_children = true\n"
             "Plain block has_children = false\n"
             "-> Children mismatch: +20 points\n\n"
             "Total = 50 + 30 + 20 = 100\n"
             "100 >= 50 -> High Risk"),
            ("answer",
             '{\n'
             '  "page_title": "Tuscan kale",\n'
             '  "db_same_name_count": 0,\n'
             '  "risk_score": 100,\n'
             '  "risk_level": "High Risk"\n'
             '}'),
        ],
    },
    # ── 4. Slack Compliance ───────────────────────────────────────────
    {
        "title": "Compliance Inspection",
        "file": "demo_slack.mp4",
        "l1": "Social Media & Community",
        "l2": "Social Network Integration",
        "l3": "Slack Workspace Automation Server",
        "steps": [
            ("user",
             "Compliance inspection:\n"
             "Reported message at ts=1512104434.000490\n"
             "Correlate with user U123ABC456 in CSV.\n"
             "Check W012A3CDE login status and\n"
             "whether W07QCRPA4 is in contacts.\n"
             "Output triage JSON with similarity score,\n"
             "time diff, and comment for issue #17\n"
             "in spengler/slack-triage."),
            ("fn",
             'get_message_by_ts(\n'
             '  ts="1512104434.000490"\n'
             ')'),
            ("tool",
             "{'status': 'success',\n"
             " 'message': {\n"
             "  'type': 'message',\n"
             "  'user': 'U222BBB222',\n"
             "  'text': 'What, you want to\n"
             "   smell my shoes better?',\n"
             "  'ts': '1512104434.000490'}}"),
            ("fn",
             'get_user_by_id(\n'
             '  user_id="U222BBB222"\n'
             ')'),
            ("tool",
             "{'status': 'not_found',\n"
             " 'message': 'User ID not found'}"),
            ("fn",
             'filter_message_csv_by_user(\n'
             '  user_id="U123ABC456"\n'
             ')'),
            ("tool",
             "{'status': 'success',\n"
             " 'rows': [{\n"
             "  'message_id': '1512085950.000216',\n"
             "  'user_id': 'U123ABC456',\n"
             "  'text': 'I find you punny and\n"
             "   would like to smell your\n"
             "   nose letter',\n"
             "  'timestamp': '1512085950.000216'\n"
             " }]}"),
            ("fn",
             'get_login_status(\n'
             '  user_id="W012A3CDE"\n'
             ')'),
            ("tool",
             "{'status': 'success',\n"
             " 'login_status': {\n"
             "  'user_id': 'W012A3CDE',\n"
             "  'is_logged_in': True,\n"
             "  'last_login':\n"
             "   '2025-06-28T12:00:00Z'}}"),
            ("fn", "list_contacts()"),
            ("tool",
             "{'status': 'success',\n"
             " 'contacts': [{\n"
             "  'owner_id': 'W012A3CDE',\n"
             "  'contact_id': 'W07QCRPA4',\n"
             "  'added_at':\n"
             "   '2025-06-28T12:05:00Z'}]}"),
            ("think",
             "Sender U222BBB222 not found\n"
             "  -> possibly deleted account\n\n"
             "Shared keywords: 'smell'\n"
             "Jaccard similarity = 3/17 ~ 0.18\n"
             "Time diff = 1512104434 - 1512085950\n"
             "  = 18484 seconds\n\n"
             "W012A3CDE is logged in\n"
             "Contact W07QCRPA4 already exists\n"
             "  -> need_add_contact = false\n\n"
             "Low similarity + deleted sender\n"
             "  -> triage level: ignore"),
            ("answer",
             '{\n'
             '  "report_sender_id": "U222BBB222",\n'
             '  "similarity_score": 0.18,\n'
             '  "time_diff_seconds": 18484,\n'
             '  "need_add_contact": false,\n'
             '  "triage_comment_body":\n'
             '    "Branch: triage-U123ABC456-\n'
             '     1512104434\\n'\
             '     Similarity: 0.18\\n'\
             '     Time Diff: 18484s\\n'\
             '     Level: ignore\\n'\
             '     Add Contact: false"\n'
             '}'),
        ],
    },
    # ── 5. Population Data ────────────────────────────────────────────
    {
        "title": "City Influence Index",
        "file": "demo_population.mp4",
        "l1": "Search & Information Retrieval",
        "l2": "API Gateway & Aggregation",
        "l3": "Population Data Server",
        "steps": [
            ("user",
             "Get top 10 cities by population plus\n"
             "Karachi (Pakistan) as candidate pool.\n"
             "Compute S = ln(population / 40).\n"
             "Karachi gets growth bonus: S * (1+growthRate).\n"
             "Get Tokyo & Mumbai population percentages.\n"
             "Find the highest scoring city.\n"
             "Convert to magnitude M = log2(S) / log2(10).\n"
             "Return JSON: winner_city, winner_country,\n"
             "score_S (4 decimals), magnitude_M (4 decimals)."),
            ("fn",
             "list_top_cities_by_population(\n"
             "  limit=10\n"
             ")"),
            ("tool",
             "[{'City': 'Tokyo', 'Country': 'Japan',\n"
             "  'Pop2023': 37194104, 'rank': 1},\n"
             " {'City': 'Delhi', 'Country': 'India',\n"
             "  'Pop2023': 32941308, 'rank': 2},\n"
             " {'City': 'Shanghai', 'Country': 'China',\n"
             "  'Pop2023': 29210808, 'rank': 3},\n"
             " {'City': 'Dhaka', 'Pop2023': 23209616},\n"
             " {'City': 'Sao Paulo', 'Pop2023': 22619736},\n"
             " {'City': 'Mexico City', 'Pop2023': 22281442},\n"
             " {'City': 'Cairo', 'Pop2023': 22183200},\n"
             " {'City': 'Beijing', 'Pop2023': 21766214},\n"
             " {'City': 'Mumbai', 'Pop2023': 21296516},\n"
             " {'City': 'Osaka', 'Pop2023': 19013434}]"),
            ("fn",
             'get_city_population(\n'
             '  city="Karachi",\n'
             '  country="Pakistan"\n'
             ')'),
            ("tool",
             "{'City': 'Karachi',\n"
             " 'Country': 'Pakistan',\n"
             " 'Continent': 'Asia',\n"
             " 'Pop2023': 17236230,\n"
             " 'Pop2022': 16839950,\n"
             " 'growthRate': 0.0235,\n"
             " 'rank': 12}"),
            ("fn",
             'get_city_population_percentage(\n'
             '  city="Tokyo"\n'
             ')'),
            ("tool", "1.797993193834086"),
            ("fn",
             'get_city_population_percentage(\n'
             '  city="Mumbai"\n'
             ')'),
            ("tool", "1.0294908789946577"),
            ("fn", "get_logarithms_for_value(x=40)"),
            ("tool",
             "{'log10': 1.60206,\n"
             " 'log2': 5.321928,\n"
             " 'ln': 3.688879}"),
            ("fn", "get_logarithms_for_value(x=10)"),
            ("tool",
             "{'log10': 1,\n"
             " 'log2': 3.321928,\n"
             " 'ln': 2.302585}"),
            ("think",
             "ln(40) = 3.688879\n"
             "log2(10) = 3.321928\n\n"
             "Tokyo: S = ln(37194104/40) ~ 13.7423\n"
             "Delhi:  S = ln(32941308/40) ~ 13.6200\n"
             "Karachi: S = ln(17236230/40) * 1.0235\n"
             "         ~ 12.97 * 1.0235 ~ 13.275\n\n"
             "Tokyo has highest S.\n"
             "M = log2(13.7423) / 3.321928\n"
             "  ~ 3.78 / 3.321928 ~ 1.1384"),
            ("answer",
             '{\n'
             '  "winner_city": "Tokyo",\n'
             '  "winner_country": "Japan",\n'
             '  "score_S": 13.7423,\n'
             '  "magnitude_M": 1.1384\n'
             '}'),
        ],
    },
    # ── 6. Telecom Support ────────────────────────────────────────────
    {
        "title": "Mobile Network Diagnosis",
        "file": "demo_telecom.mp4",
        "l1": "Communication & General Utilities",
        "l2": "Messaging & Notification",
        "l3": "Telecom API MCP Server",
        "steps": [
            ("user",
             "My mobile data isn't working properly.\n"
             "Sometimes it just stops, and other times\n"
             "it's really slow. I need excellent\n"
             "internet speed on my phone.\n"
             "My phone number is 555-123-2002."),
            ("fn",
             'get_customer_by_phone(\n'
             '  phone_number="555-123-2002"\n'
             ')'),
            ("tool",
             '{"customer_id": "C1001",\n'
             ' "full_name": "John Smith",\n'
             ' "email": "john.smith@example.com",\n'
             ' "phone_number": "555-123-2002",\n'
             ' "account_status": "Active",\n'
             ' "line_ids": ["L1001","L1002","L1003"],\n'
             ' "payment_methods": [{\n'
             '   "type": "Credit Card",\n'
             '   "last_4": "1235"}]}'),
            ("fn",
             'get_details_by_id(\n'
             '  id="L1002"\n'
             ')'),
            ("tool",
             '{"line_id": "L1002",\n'
             ' "phone_number": "555-123-2002",\n'
             ' "status": "Active",\n'
             ' "plan_id": "P1002",\n'
             ' "device_id": "D1002",\n'
             ' "data_used_gb": 8.7,\n'
             ' "roaming_enabled": true}'),
            ("fn",
             'get_details_by_id(\n'
             '  id="P1002"\n'
             ')'),
            ("tool",
             '{"plan_id": "P1002",\n'
             ' "name": "Premium Plan",\n'
             ' "data_limit_gb": 15.0,\n'
             ' "price_per_month": 65.0,\n'
             ' "data_refueling_price_per_gb": 2.0}'),
            ("think",
             "Data usage 8.7 / 15 GB = within limit.\n"
             "Line status: Active, plan: Premium.\n\n"
             "Checking network settings:\n"
             "- Network mode: 2G only (slow!)\n"
             "- Airplane mode: enabled\n"
             "- Mobile data: disabled\n\n"
             "Root causes identified:\n"
             "1. Network mode set to 2G only\n"
             "2. Airplane mode was on\n"
             "3. Mobile data was off"),
            ("user",
             "I changed network mode to 4G/5G preferred,\n"
             "turned off Airplane Mode,\n"
             "and enabled mobile data.\n"
             "Speed test shows 275 Mbps.\n"
             "Connection is now very fast!"),
            ("answer",
             "Issue resolved!\n\n"
             "Root causes:\n"
             "1. Network mode was '2G only'\n"
             "   -> Changed to 4G/5G preferred\n"
             "2. Airplane mode was enabled\n"
             "   -> Toggled off\n"
             "3. Mobile data was disabled\n"
             "   -> Enabled\n\n"
             "Result: 275 Mbps download (Excellent)\n"
             "5G connectivity with excellent signal"),
        ],
    },
    # ── 7. Twitter Engagement ─────────────────────────────────────────
    {
        "title": "Engagement Value Audit",
        "file": "demo_twitter.mp4",
        "l1": "Social Media & Community",
        "l2": "Social Network Integration",
        "l3": "Twitter MCP Server",
        "steps": [
            ("user",
             "Log in as TwitterDev and perform an\n"
             "engagement value audit:\n"
             "1. Verify profile consistency\n"
             "   (username, id, name, protected, created_at)\n"
             "2. Find highest influence score\n"
             "   (followers/following) in my following list\n"
             "3. Check tweet_id=2 comments:\n"
             "   ratio of comments from followed users\n"
             "Return JSON with profile_consistency,\n"
             "top_influence_user, top_influence_score,\n"
             "tweet2_comment_ratio,\n"
             "has_following_comment."),
            ("fn",
             'get_user_by_username(\n'
             '  username="TwitterDev"\n'
             ')'),
            ("tool",
             "{'id': '2244994945',\n"
             " 'id_str': '2244994945',\n"
             " 'name': 'X Dev',\n"
             " 'username': 'TwitterDev',\n"
             " 'location': '127.0.0.1',\n"
             " 'protected': False,\n"
             " 'followers_count': 513958,\n"
             " 'friends_count': 2039,\n"
             " 'verified': True,\n"
             " 'created_at':\n"
             "  'Sat Dec 14 04:35:55 +0000 2013'}"),
            ("fn", "list_following()"),
            ("tool",
             "[{'created_at': '2013-12-14T04:35:55Z',\n"
             "  'id': '2244994945',\n"
             "  'name': 'X Dev',\n"
             "  'protected': False,\n"
             "  'username': 'TwitterDev'}]"),
            ("fn",
             'get_comments_for_tweet(\n'
             '  tweet_id="2"\n'
             ')'),
            ("tool",
             "[{'id': 20, 'TweetId': 2,\n"
             "  'UserId': 1,\n"
             "  'comment': 'comment',\n"
             "  'User': {'name': 'user1',\n"
             "   'account': 'user1'},\n"
             "  'replyTo': 'User1'}]"),
            ("think",
             "Profile consistency check:\n"
             "username, id, name, protected, created_at\n"
             "all present and match -> true\n\n"
             "Following list: only TwitterDev itself\n"
             "Influence = 513958 / 2039 = 252.06\n\n"
             "Tweet #2 comments: 1 comment by 'user1'\n"
             "'user1' is NOT in following list\n"
             "-> ratio = 0/1 = 0\n"
             "-> has_following_comment = false"),
            ("answer",
             '{\n'
             '  "profile_consistency": true,\n'
             '  "top_followed_influence_user":\n'
             '    "TwitterDev",\n'
             '  "top_followed_influence_score":\n'
             '    252.0637,\n'
             '  "tweet2_following_comment_ratio": 0,\n'
             '  "tweet2_has_comment_from_following":\n'
             '    false\n'
             '}'),
        ],
    },
    # ── 8. GitHub Admin ───────────────────────────────────────────────
    {
        "title": "Repository Management",
        "file": "demo_github.mp4",
        "l1": "System & Cloud Infrastructure",
        "l2": "Cloud Platform Services",
        "l3": "GitHub",
        "steps": [
            ("user",
             "I've just been promoted!\n"
             "Please complete these admin tasks:\n\n"
             "1. Update username: adryzz -> adryzzVP\n"
             "2. Email: adryzzVP@users.noreply.github.com\n"
             "3. Upgrade role to owner\n"
             "4. Make all my repos private\n"
             "5. Create new private repo:\n"
             "   VPTeamFormation (branch: team1)"),
            ("fn",
             'getUserByUsername(\n'
             '  username="adryzz"\n'
             ')'),
            ("tool",
             '{"id": 1166,\n'
             ' "username": "adryzz",\n'
             ' "email":\n'
             '  "adryzz@users.noreply.github.com",\n'
             ' "role": "collaborator",\n'
             ' "created_at":\n'
             '  "2021-11-25T15:07:36+00:00"}'),
            ("fn",
             'updateUser(\n'
             '  id="1166",\n'
             '  user_id="1166",\n'
             '  username="adryzzVP",\n'
             '  email="adryzzVP@users.\n'
             '    noreply.github.com",\n'
             '  role="owner"\n'
             ')'),
            ("tool",
             '{"id": 1166,\n'
             ' "username": "adryzzVP",\n'
             ' "email": "adryzzVP@users.\n'
             '  noreply.github.com",\n'
             ' "role": "owner"}'),
            ("fn",
             'getRepositories(\n'
             '  owner_id="1166"\n'
             ')'),
            ("tool",
             '{"repositories": [{\n'
             '  "id": 160,\n'
             '  "name": "Ibralogue",\n'
             '  "owner_id": 1166,\n'
             '  "owner_username": "adryzzVP",\n'
             '  "is_private": false,\n'
             '  "default_branch": "main"}],\n'
             ' "pagination": {"total": 1}}'),
            ("fn",
             'updateRepository(\n'
             '  id="160",\n'
             '  user_id="1166",\n'
             '  is_private=true\n'
             ')'),
            ("tool",
             '{"id": 160,\n'
             ' "name": "Ibralogue",\n'
             ' "is_private": true}'),
            ("fn",
             'createRepository(\n'
             '  name="VPTeamFormation",\n'
             '  owner_id="1166",\n'
             '  user_id="1166",\n'
             '  is_private=true,\n'
             '  default_branch="team1"\n'
             ')'),
            ("tool",
             '{"id": 161,\n'
             ' "name": "VPTeamFormation",\n'
             ' "owner_id": "1166",\n'
             ' "owner_username": "adryzzVP",\n'
             ' "is_private": true,\n'
             ' "default_branch": "team1",\n'
             ' "created_at":\n'
             '  "2026-01-19 23:13:10"}'),
            ("answer",
             "All tasks completed:\n\n"
             "1. Username: adryzz -> adryzzVP\n"
             "   Email: adryzzVP@...github.com\n"
             "   Role: collaborator -> owner\n\n"
             "2. Repository Ibralogue\n"
             "   -> set to private\n\n"
             "3. New repo VPTeamFormation created\n"
             "   Private, default branch: team1"),
        ],
    },
    # ── 9. Document Governance ────────────────────────────────────────
    {
        "title": "Database Governance",
        "file": "demo_document.mp4",
        "l1": "Document & Design",
        "l2": "Office & Text Processing",
        "l3": "Document Operations Server",
        "steps": [
            ("user",
             "Travel database governance check:\n"
             "1. Verify user e79a0b74-3aba-4149-\n"
             "   9f74-0bb5791a6ee6 name\n"
             "2. Check database c3f0603a-3cd3-55fa-\n"
             "   c8df-gc1gg8e0a4d5 status property\n"
             "   against tag category standards\n"
             "3. Count databases with status-type\n"
             "   select properties\n"
             "4. Calculate exact match ratio\n"
             "Return JSON with report_owner_name,\n"
             "travel_db_status_property_name,\n"
             "recommended_status_category_name,\n"
             "status_named_exact_match_ratio_percent."),
            ("fn",
             'get_user_by_id(\n'
             '  user_id="e79a0b74-3aba-\n'
             '    4149-9f74-0bb5791a6ee6"\n'
             ')'),
            ("tool",
             "{'object': 'user',\n"
             " 'id': 'e79a0b74-3aba-...',\n"
             " 'type': 'person',\n"
             " 'name': 'Avocado Lovelace',\n"
             " 'person': {\n"
             "  'email': 'avocado@example.org'}}"),
            ("fn",
             'get_database_by_id(\n'
             '  database_id="c3f0603a-3cd3-\n'
             '    55fa-c8df-gc1gg8e0a4d5"\n'
             ')'),
            ("tool",
             "{'title': 'Travel Itineraries',\n"
             " 'properties': {\n"
             "  'Title': {'title': {}},\n"
             "  'Traveler': {'people': {}},\n"
             "  'Status': {'select': {'options':\n"
             "   [{'name': 'Planned', 'color': 'blue'},\n"
             "    {'name': 'Booked', 'color': 'green'},\n"
             "    {'name': 'Completed', 'color': 'gray'},\n"
             "    {'name': 'Cancelled', 'color': 'red'}\n"
             "  ]}},\n"
             "  'Policy': {'relation': {...}}}}"),
            ("fn", "list_tag_categories()"),
            ("tool",
             "['Status', 'Department',\n"
             " 'Quarter', 'Travel Status',\n"
             " 'Category', 'General Tags']"),
            ("fn", "list_databases()"),
            ("tool",
             "[{title: 'Onboarding Tasks',\n"
             "  properties: {Status: select}},\n"
             " {title: 'Quarterly Reviews',\n"
             "  properties: {Quarter: select}},\n"
             " {title: 'Travel Itineraries',\n"
             "  properties: {Status: select}},\n"
             " {title: 'SOP Library',\n"
             "  properties: {Category: select}}]"),
            ("think",
             "Travel DB status property = 'Status'\n"
             "Tag categories include 'Status'\n"
             "-> Direct match, compliant.\n\n"
             "Status-type databases:\n"
             "- Onboarding Tasks: 'Status' (exact)\n"
             "- Travel Itineraries: 'Status' (exact)\n"
             "(Quarter and Category are not status-type)\n\n"
             "2 databases with status-type select\n"
             "2/2 exact match = 100.0%"),
            ("answer",
             '{\n'
             '  "report_owner_name":\n'
             '    "Avocado Lovelace",\n'
             '  "travel_db_status_property_name":\n'
             '    "Status",\n'
             '  "recommended_status_category_name":\n'
             '    "Status",\n'
             '  "status_named_exact_match_\n'
             '    ratio_percent": 100.0\n'
             '}'),
        ],
    },
]

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    total = len(DEMOS)
    for i, demo in enumerate(DEMOS, 1):
        out = os.path.join(base, demo["file"])
        print(f"\n{'='*60}")
        print(f"[{i}/{total}] {demo['title']}  ->  {demo['file']}")
        print(f"{'='*60}")
        generate_video_for(
            demo["title"], demo["steps"], out,
            l1=demo.get("l1", ""),
            l2=demo.get("l2", ""),
            l3=demo.get("l3", ""),
        )
    print(f"\n All {total} videos generated!")
