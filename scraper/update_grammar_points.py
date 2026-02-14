import json
from bs4 import BeautifulSoup
import requests

def update_grammar_points(output_path="grammar_points.json", url="https://bunpro.jp/grammar_points"):
    """
    Updates the grammar points JSON file by fetching the index in memory.
    """
    print(f"Fetching grammar index from {url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        print("Successfully fetched grammar index.")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    n_levels = {
        'N5': [],
        'N4': [],
        'N3': [],
        'N2': [],
        'N1': [],
        'Non-JLPT': []
    }

    tiles = soup.select('li[data-grammar-point]')
    print(f"Found {len(tiles)} grammar point tiles.")

    for tile in tiles:
        name = tile.get('data-grammar-point')
        link_tag = tile.select_one('a')
        if not link_tag:
            continue
        url_gp = link_tag.get('href')
        
        # Determine level
        classes = tile.get('class', [])
        level = None
        for cls in classes:
            if cls.startswith('js_search-option_jlpt'):
                lvl_code = cls.replace('js_search-option_jlpt', '')
                if lvl_code == 'NT':
                    level = 'Non-JLPT'
                elif lvl_code.startswith('N'):
                    level = lvl_code
                break
        
        if level in n_levels:
            n_levels[level].append({name: url_gp})

    # Print counts
    for level, points in n_levels.items():
        print(f"Level {level}: {len(points)} points")

    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(n_levels, f, ensure_ascii=False, indent=4)
    
    print(f"Updated JSON saved to {output_path}")

if __name__ == "__main__":
    update_grammar_points()
