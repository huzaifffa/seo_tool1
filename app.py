from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sitemap_url = request.form['url']
        response = requests.get(sitemap_url)
        urls = extract_urls_from_sitemap(response.content)

        results = []
        for url in urls:
            title, meta_description = fetch_metadata(url)
            title_improvement = suggest_title_improvement(title)
            meta_description_improvement = suggest_meta_description_improvement(meta_description)
            results.append({
                'url': url,
                'title': title,
                'meta_description': meta_description,
                'title_improvement': title_improvement,
                'meta_description_improvement': meta_description_improvement
            })

        return render_template('results.html', results=results)
    return render_template('form.html')

def extract_urls_from_sitemap(xml_content):
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    root = ET.fromstring(xml_content)
    urls = [url.find('ns:loc', namespace).text for url in root.findall('ns:url', namespace)]
    return urls

def fetch_metadata(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.string if soup.title else 'No title found'
    meta_description = 'No meta description found'
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_desc_tag:
        meta_description = meta_desc_tag.get('content', 'No content attribute found')
    return title, meta_description

def suggest_title_improvement(title):
    improvements = []
    if len(title) < 40:
        improvements.append(f"The title is too short. Its currently {len(title)} characters. Consider increasing it to at least 40 characters.")
    elif len(title) > 60:
        improvements.append(f"The title is too long. Its currently {len(title)} characters. Consider keeping it under 60 characters.")
    return improvements if improvements else [f"The title looks good! Its current length is {len(title)} characters."]

def suggest_meta_description_improvement(meta_description):
    improvements = []
    if len(meta_description) < 50:
        improvements.append(f"The meta description is too short. Its currently {len(meta_description)} characters. Consider increasing it to at least 50 characters.")
    elif len(meta_description) > 160:
        improvements.append(f"The meta description is too long. Its currently {len(meta_description)} characters. Consider keeping it under 160 characters.")
    return improvements if improvements else [f"The meta description looks good! Its current length is {len(meta_description)} characters."]

if __name__ == '__main__':
    app.run(debug=True)
