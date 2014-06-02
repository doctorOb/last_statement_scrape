from bs4 import BeautifulSoup
import urllib
import json

BASE_URL = "http://www.tdcj.state.tx.us/death_row/"
LISTINGS = "http://www.tdcj.state.tx.us/death_row/dr_executed_offenders.html"

def _GET(url):
	try:
		page = urllib.urlopen(url)
		return page.read()
	except IOError: #connection unsuccessful
		return None

def parse_list_entry(row):
	tds = row.find_all(True)

	ret = dict()
	ret['offender_link'] = tds[2].get('href')
	ret['statement_link'] = tds[4].get('href')
	ret['last_name'] = tds[5].get_text()
	ret['first_name'] = tds[6].get_text()
	ret['age'] = tds[8].get_text()
	ret['race'] = tds[10].get_text()
	return ret

def get_listings():
	page = _GET(LISTINGS)
	soup = BeautifulSoup(page)

	entries = soup.find_all('tr')
	listings = {'raw': []}
	for entry in list(entries)[1:]:
		listings['raw'].append(parse_list_entry(entry))

	with open('listings.json','w') as out:
		json.dump(listings,out)

def get_last_statement(url):
	page = _GET(BASE_URL + url)
	soup = BeautifulSoup(page)

	ps = soup.find_all('p')
	statement = ""
	for p in ps:
		content = p.get_text().encode('ascii','ignore')
		if len(content) < 50:
			continue
		statement += " {}".format(content)

	return statement


if __name__ == '__main__':

	listings = None
	with open('listings.json','r') as inf:
		listings = json.load(inf)

	entries = listings['raw']
	statement_json = {'all': []}
	i = 0
	for entry in listings['raw']:
		print "on entry {}".format(i)
		statement = get_last_statement(entry['statement_link'])
		statement_json['all'].append({
			'first_name': entry['first_name'],
			'last_name': entry['last_name'],
			'age': entry['age'],
			'race': entry['race'],
			'statement': statement
		})
		i+=1

	with open('statements.json','w') as out:
		json.dump(statement_json,out)







