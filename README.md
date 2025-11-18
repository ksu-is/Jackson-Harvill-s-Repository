@ -1,36 +0,0 @@
# ScoutSense
ScoutSense is a Python-powered sports analytics platform designed to simulate, predict, and visualize NFL draft strategies. Built by a passionate fan of football and data, this project bridges the gap between sports enthusiasm and technical innovation — empowering users to play GM, challenge expert mock drafts, and explore team-building philosophies through data.

Project Motivation
As a lifelong sports fan — especially of football — I’ve always been fascinated by the depth of data behind team decisions. The NFL Draft is my favorite time of year, and I spend months analyzing stats and watching film. ScoutSense is my way of connecting that passion to my career in information systems and software development.
Inspired by projects like NFL Draft Prospect Predictor by Brandon Pestana and GitHub user rlosito95, and guided by educational resources on Python and APIs, ScoutSense aims to be a multi-layered system that combines data scraping, machine learning, and interactive visualization.

Project Goals
- Scrape mock draft data from sites like Tankathon using BeautifulSoup (BS4)
- Ingest player profiles, combine metrics, and historical performance data from sources like ESPN and Pro Football Reference
- Predict:
- Best team-to-player fits using classification models (e.g., Random Forest)
- Draft pick number based on aggregated metrics
- Visualize:
- Team strategies and draft philosophies (e.g., BPA vs. positional need)
- What-if scenarios and simulated mock drafts
- Deliver an interactive dashboard using Streamlit

Target Users
- NFL fans who want to simulate mock drafts and explore team-building strategies
- Sports analysts seeking data-driven insights into draft decisions
- Fantasy football players looking to predict rookie impact
- Students and developers curious about how coding and sports analytics intersect

Features
- Real-time mock draft scraping
- Prospect evaluation engine
- Draft pick prediction
- Team strategy simulation
- Interactive dashboard for exploration

Development Notes
- This is a solo project.
- The system will be modular to allow future expansion (e.g., adding more sports or deeper analytics).
- Initial focus will be on building a working prototype with scraping, prediction, and basic visualization.
