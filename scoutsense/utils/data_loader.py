#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFL Draft Data Loader and Scraper
Loads and processes NFL draft data from pro-football-reference.com
"""

import urllib.request
from bs4 import BeautifulSoup
import csv
import time
import pandas as pd

def scrape_draft_year(year):
    """Scrape draft data for a given year from Pro Football Reference"""
    url = f"https://www.pro-football-reference.com/years/{year}/draft.htm"
    players = []
    
    print(f"Fetching draft data for {year} from {url}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read()
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"ERROR: Failed to fetch {url}: {e}")
        return players
    
    # Find the draft table
    table = soup.find('table', {'id': 'drafts'})
    if not table:
        print("ERROR: Could not find draft table on page")
        return players
    
    tbody = table.find('tbody')
    if not tbody:
        print("ERROR: Could not find table body")
        return players
    
    rows = tbody.find_all('tr')
    print(f"Found {len(rows)} rows in draft table")
    
    for row in rows:
        cols = row.find_all('td')
        
        # Skip rows with fewer than 10 columns or header rows
        if len(cols) < 10:
            continue
        
        try:
            player = {
                "Draft Pick": cols[0].get_text(strip=True),
                "Team": cols[1].get_text(strip=True),
                "Name": cols[2].get_text(strip=True),
                "Pos": cols[3].get_text(strip=True),
                "Age": cols[4].get_text(strip=True),
                "Ht": cols[5].get_text(strip=True),
                "Wt": cols[6].get_text(strip=True),
                "College": cols[7].get_text(strip=True),
                "College/Yrs": cols[8].get_text(strip=True),
                "Meets": cols[9].get_text(strip=True) if len(cols) > 9 else "",
            }
            players.append(player)
        except Exception as e:
            print(f"Warning: Could not parse row: {e}")
            continue
    
    return players

def load_draft_data(csv_file='nfl_draft_data.csv'):
    """Load NFL draft data from CSV file and return as DataFrame"""
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df['draft_pick'] = pd.to_numeric(df['draft_pick'], errors='coerce')
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    return df

def main():
    # Scrape multiple years (2009-2023 as examples)
    # Modify the range as needed
    start_year = 2009
    end_year = 2023  # Change this to scrape more/fewer years
    
    all_players = []
    
    for year in range(start_year, end_year + 1):
        print(f"\n--- Scraping {year} Draft ---")
        players = scrape_draft_year(year)
        if players:
            print(f"Successfully scraped {len(players)} players from {year} draft")
            all_players.extend(players)
        else:
            print(f"No data found for {year} draft")
        
        # Be polite: wait between requests
        time.sleep(1)
    
    if not all_players:
        print("\nNo players were scraped. Exiting.")
        return
    
    print(f"\n--- Total players scraped: {len(all_players)} ---")
    
    # Print first player as verification
    if all_players:
        print(f"\nFirst player: {all_players[0]}")
    
    # Write to CSV
    csv_file = 'nfl_draft_data.csv'
    print(f"\nWriting {len(all_players)} players to {csv_file}")
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if all_players:
                fieldnames = all_players[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_players)
        print(f"Successfully wrote to {csv_file}")
    except Exception as e:
        print(f"ERROR: Failed to write CSV: {e}")

if __name__ == "__main__":
    main()
