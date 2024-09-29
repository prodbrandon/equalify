import requests
from bs4 import BeautifulSoup
from tqdm import tqdm  # Import the tqdm library for the progress bar

# Step 1: Make requests to the website for multiple pages
base_url = 'https://scholarships.asu.edu/scholarship-search&page='
urls = [f'{base_url}{i}' for i in range(0, 8)]  # Generate URLs for pages 0 to 7

links = []

# Loop through each page URL
for url in urls:
    response = requests.get(url)

    # Step 2: Parse the content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Step 3: Find all the links on the page
    for link in soup.find_all('a', href=True):  # Find all anchor tags with href attribute
        href = link['href']

        # Make sure the link is complete (handle relative URLs)
        if href.startswith('http'):
            links.append(href)
        else:
            # If the link is relative, convert it to an absolute URL
            full_url = requests.compat.urljoin(url, href)
            links.append(full_url)

# Step 4: Only include links with the pattern "https://scholarships.asu.edu/scholarship/" followed by numbers
filtered_links = [link for link in links if link.startswith('https://scholarships.asu.edu/scholarship/')]

# New lists to store ID numbers and HTML descriptions
id_numbers = []
html_descriptions = []

# Step 5: Extract ID numbers and scrape each filtered link for its HTML description using div parent method
for link in tqdm(filtered_links, desc="Scraping scholarship pages"):  # Add a progress bar to the loop
    # Extract the ID number (assumes ID is at the end of the URL after the last '/')
    id_number = link.split('/')[-1]
    id_numbers.append(id_number)

    # Make a request to the individual scholarship page to get its content
    response = requests.get(link)
    scholarship_soup = BeautifulSoup(response.content, 'html.parser')

    # Find the h1 element with id "page-title" to locate the relevant div
    h1_element = scholarship_soup.find('h1', id='page-title')

    if h1_element:
        # Find the parent div of the h1 element (assuming description is within the same div)
        parent_div = h1_element.find_parent('div')

        if parent_div:
            # Get the text content of the parent div (this should contain the description)
            description = parent_div.get_text(strip=True, separator=' ')
            html_descriptions.append(description)
        else:
            html_descriptions.append("Parent div not found")
    else:
        html_descriptions.append("H1 element with id 'page-title' not found")

# Print the results
print("ID Numbers:", id_numbers)
print("HTML Descriptions:", html_descriptions)