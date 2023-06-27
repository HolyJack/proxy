from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

target_url = "https://news.ycombinator.com"
proxy_url = "localhost"
symbol_to_add = "™"
session = requests.Session()

def scrape_website(url, method):
    headers = {'User-Agent': request.headers.get('User-Agent')}

    if method=='POST':
        response = session.post(url, headers=headers, data=request.form)
    else:
        response = session.get(url, headers=headers)

    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.content, 'html.parser')

    # Update CSS file URLs
    css_links = soup.select('link[rel="stylesheet"]')
    for css_link in css_links:
        css_url = urljoin(url, css_link['href'])
        css_link['href'] = css_url

    # Update image URLs
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        img_src = urljoin(url, img_tag['src'])
        img_tag['src'] = img_src

    # Update internal links
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        if 'href' in a_tag.attrs and (a_tag['href'].startswith(target_url) or not a_tag['href'].startswith('http')):
            href = urljoin(url, a_tag['href'])
            a_tag['href'] = href[len(target_url):]

    for text_node in soup.find_all(text=True):
        words = text_node.split()
        modified_words = [word + symbol_to_add if len(word) == 6 else word for word in words]
        text_node.replace_with(' '.join(modified_words))

    return soup.prettify()

@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path=''):

    url = urljoin(target_url, path)
    if request.args: url += "?" + urlencode(request.args)
    
    content = scrape_website(url, request.method)

    return render_template('index.html', content=content)

if __name__ == '__main__':
    app.run()
