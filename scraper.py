import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Function to fetch and parse content from a given URL
def scrape_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract entry title
        entry_title_tag = soup.find(class_="entry-title")
        if entry_title_tag:
            entry_title_text = entry_title_tag.get_text().strip()
            # Split the title by ' at ' and get the first part
            file_name = entry_title_text.split(' at')[0].strip()
        else:
            print(f"Entry title not found for URL: {url}")
            return

        # Extract image content
        right_img_tag = soup.find(class_="right-img")
        if right_img_tag:
            # Check if the tag is an image and has a 'src' attribute
            img_tag = right_img_tag.find('img')
            if img_tag and img_tag.get('src'):
                img_url = urljoin(url, img_tag['src'])  # Get full image URL
                # Save the image
                save_image(file_name, img_url)
            else:
                print(f"No image found in 'right-img' class for URL: {url}")
        else:
            print(f"Right-img class not found for URL: {url}")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

# Function to save the image from the given URL
def save_image(file_name, img_url):
    # Create a directory to save the images if it doesn't exist
    save_dir = "static/images"
    os.makedirs(save_dir, exist_ok=True)
    
    # Define the path where the image will be saved
    img_ext = img_url.split('.')[-1]  # Get image extension (jpg, png, etc.)
    file_path = os.path.join(save_dir, f"{file_name}.{img_ext}")
    
    # Download the image
    img_response = requests.get(img_url)
    if img_response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(img_response.content)  # Save image content to file
        print(f"Image saved as: {file_path}")
    else:
        print(f"Failed to download image from {img_url}")

# Main function to process multiple URLs
def scrape_multiple_urls(url_list):
    for url in url_list:
        print(f"Processing URL: {url}")
        scrape_url(url)

# Function to load URLs from a CSV file
def load_urls_from_csv(csv_file):
    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Extract the 'url_for_product' column and drop NaN values
    urls = df['url_for_product'].dropna().tolist()
    
    return urls

# Main execution
if __name__ == "__main__":
    # Specify the path to the CSV file
    csv_file_path = 'mcdonalds_dataset.csv'  # Replace with the actual path to your CSV file
    
    # Load the URLs from the CSV file
    urls = load_urls_from_csv(csv_file_path)
    
    # Start the scraping process
    scrape_multiple_urls(urls)
