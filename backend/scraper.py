import requests
from bs4 import BeautifulSoup
from database import save_sales

def scrape_amazon_product(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    sales_elem = soup.select_one('[data-feature-name="purchaseCount"]') or soup.find('span', string=lambda t: t and 'bought' in t.lower())
    if sales_elem:
        sold = int(''.join(filter(str.isdigit, sales_elem.text)))
    else:
        sold = 0
    
    save_sales(url, sold)
    return sold
