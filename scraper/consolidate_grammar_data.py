import os
import json
import re
from tqdm import tqdm

def extract_next_data():
    # Set up paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    pages_dir = os.path.join(project_root, 'grammar_pages')
    output_file = os.path.join(script_dir, 'grammar_data_consolidated.json')
    
    if not os.path.exists(pages_dir):
        print(f"Error: Directory not found: {pages_dir}")
        return

    # List all HTML files
    html_files = [f for f in os.listdir(pages_dir) if f.endswith('.html')]
    print(f"Found {len(html_files)} HTML files in {pages_dir}")
    
    all_data = []
    
    # Regex to extract content inside <script id="__NEXT_DATA__">
    # Matches the script tag and captures everything inside
    next_data_re = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL)
    
    for filename in tqdm(html_files, desc="Extracting JSON"):
        file_path = os.path.join(pages_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = next_data_re.search(content)
            if match:
                json_text = match.group(1)
                try:
                    data = json.loads(json_text)
                    page_props = data.get('props', {}).get('pageProps', {})
                    reviewable = page_props.get('reviewable', {})
                    
                    if reviewable:
                        # Extract only what's needed
                        # this excludes comments (latestDiscourseReplies) and 
                        # common info/errors (__namespaces)
                        grammar_point = reviewable.copy()
                        grammar_point['included'] = page_props.get('included', {})
                        grammar_point['_source_filename'] = filename
                        all_data.append(grammar_point)
                except json.JSONDecodeError as e:
                    print(f"\nJSON Decode Error in {filename}: {e}")
            else:
                print(f"\nWarning: No __NEXT_DATA__ found in {filename}")
                
        except Exception as e:
            print(f"\nError processing {filename}: {e}")
            
    # Save the collected data
    print(f"Saving {len(all_data)} items to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully extracted data to {output_file}")

if __name__ == "__main__":
    extract_next_data()
