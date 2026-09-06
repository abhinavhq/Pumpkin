"""
Test the Simple Parser
"""

from app.parser.simple_parser import SimpleParser
import requests

url = 'https://en.wikipedia.org/wiki/Artificial_intelligence'
html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text

parser = SimpleParser()
result = parser.parse(html)

print(f'Title: {result["title"]}')
print(f'Word Count: {result["word_count"]}')
if result['content']:
    print(f'Content Preview: {result["content"][:200]}...')
else:
    print('No content extracted')