# -*- coding: utf-8 -*-
"""
College Football Reference Web Scraper
Scrapes player statistics from College Football Reference website
"""
import sys
import re
try:
    import pandas as pd
    import requests
    import bs4
except ImportError:
    print("Required modules not found. Please install pandas, requests, and bs4.")
    sys.exit(1)


def pull_table(url, table_id, header=False):
    """
    Extract table data from a College Football Reference page.
    
    Args:
        url: URL of the page to scrape
        table_id: HTML id of the table to extract
        header: Whether to use the table's header row as column names
        
    Returns:
        DataFrame with the extracted table data
    """
    res = requests.get(url)
    # Work around HTML comments
    comm = re.compile("<!--|-->")
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    tables = soup.findAll('table', id=table_id)
    
    if not tables:
        return pd.DataFrame()
    
    data_rows = tables[0].findAll('tr')
    game_data = [[td.getText() for td in data_rows[i].findAll(['th', 'td'])]
                 for i in range(len(data_rows))]
    data = pd.DataFrame(game_data)
    
    if header:
        data_header = tables[0].findAll('thead')
        if data_header:
            data_header = data_header[0].findAll("tr")
            if data_header:
                data_header = data_header[0].findAll("th")
                header_list = [data_header[i].getText() for i in range(len(data.columns))]
                data.columns = header_list
                # Remove duplicate header rows
                data = data.loc[data[header_list[0]] != header_list[0]]
    
    data = data.reset_index(drop=True)
    return data


def pull_links(url, table_id, header=False):
    """
    Extract hyperlinks from a table on a College Football Reference page.
    
    Args:
        url: URL of the page to scrape
        table_id: HTML id of the table to extract
        header: Whether to use the table's header row as column names
        
    Returns:
        DataFrame with hyperlinks from the table
    """
    res = requests.get(url)
    # Work around HTML comments
    comm = re.compile("<!--|-->")
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    tables = soup.findAll('table', id=table_id)
    
    if not tables:
        return pd.DataFrame()
    
    data_rows = tables[0].findAll('tr')
    game_data = [[td.get('href') for td in data_rows[i].findAll(['a'])]
                 for i in range(len(data_rows))]
    data = pd.DataFrame(game_data)
    
    if header:
        data_header = tables[0].findAll('thead')
        if data_header:
            data_header = data_header[0].findAll("tr")
            if data_header:
                data_header = data_header[0].findAll("th")
                header_list = [data_header[i].getText() for i in range(len(data.columns))]
                data.columns = header_list
                # Remove duplicate header rows
                data = data.loc[data[header_list[0]] != header_list[0]]
    
    data = data.reset_index(drop=True)
    return data


def get_column_values(dataframe, column_name):
    """
    Extract values from a specific column as a list.
    
    Args:
        dataframe: DataFrame to extract from
        column_name: Column name to extract
        
    Returns:
        List of values from the column
    """
    return dataframe[column_name].tolist()


# Example usage - Pull individual player statistics
if __name__ == "__main__":
    try:
        url_list = pd.read_csv('temp_url_list.csv')
        player_urls = get_column_values(url_list, 'cfb_reference')
        
        stat_list = []
        stat_tables = ['defense', 'rushing', 'receiving', 'kick_ret', 'punt_ret']
        
        # Column indices to extract from each stat table
        stat_columns = {
            'receiving': [0, 1, 2, 5, 6, 7, 9, 10, 11, 13],
            'rushing': [0, 1, 2, 5, 6, 7, 9, 10, 11, 13],
            'kick_ret': [0, 1, 2, 5, 6, 7, 9, 10, 11, 13],
            'punt_ret': [0, 1, 2, 5, 6, 7, 9, 10, 11, 13],
            'defense': [0, 1, 2, 5, 6, 7, 9, 10, 11, 14, 15, 19, 16, 18]
        }
        
        for url in player_urls:
            player_list = [url]
            
            for stat_table in stat_tables:
                player_list.append(stat_table)
                columns = stat_columns.get(stat_table, [])
                
                try:
                    table_data = pull_table(url, stat_table)
                    if not table_data.empty and len(table_data) > 1:
                        # Extract the last row of stats
                        for col_idx in columns:
                            if col_idx < len(table_data.columns):
                                player_list.append(table_data.iloc[len(table_data) - 2, col_idx])
                            else:
                                player_list.append('')
                    else:
                        # No data found, add empty values
                        for _ in columns:
                            player_list.append('')
                except Exception:
                    # Error fetching table, add empty values
                    for _ in columns:
                        player_list.append('')
            
            stat_list.append(player_list)
        
        # Write results to CSV
        header = ('cfb_url,defense,year,school,conf,g,tkl,ast_tkl,tfl,sk,int,int_td,pass_def,ff,fr,fr_td,'
                  'rushing,year,school,conf,g,att,yds,td,rec,yds,td,receiving,year,school,conf,g,rec,yds,td,att,yds,td,'
                  'kick_ret,year,school,conf,g,kret,kyds,ktd,pret,pyds,ptd,punt_ret,year,school,conf,g,pret,pyds,ptd,kret,kyds,ktd\n')
        
        with open('dumpfile.csv', 'w') as dumpfile:
            dumpfile.write(header)
            for row in stat_list:
                dumpfile.write(','.join(str(val) for val in row) + '\n')
        
        print(f"Successfully wrote {len(stat_list)} player records to dumpfile.csv")
        
    except FileNotFoundError:
        print("Error: temp_url_list.csv not found")
    except Exception as e:
        print(f"Error: {e}")
