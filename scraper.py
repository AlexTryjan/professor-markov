from lxml import html
import codecs
import requests
import re

def scrape_description(pkmn_name):
    pkmn_name = pkmn_name.replace(': ','-').replace(' ','-')
    page = requests.get('http://pokemondb.net/pokedex/' + pkmn_name)
    tree = html.fromstring(page.content)
    dex_entry = tree.xpath('/html/body/article/table/tbody/tr[2]/td/text()')
    return dex_entry[0]

def scrape_pokemon():
    page = requests.get('http://www.serebii.net/sunmoon/alolapokedex.shtml')
    tree = html.fromstring(page.content)
    list = tree.xpath('//a[contains(@href,\'/pokedex-sm/\')]/text()')
    cleaned_list = []
    for x in list:
        re.sub("[^a-zA-z0-9!@#,/.,#!$%^&*;:{}=-_`~( )/]+", "", x)
        cleaned_list.extend(x.splitlines())
        #cleaned_list.extend(re.findall(r'([A-Z,-])\w', x))
    return cleaned_list[1::2]

def main():
    file = codecs.open('test.txt', 'w', 'utf-8')
    pkmn_names = scrape_pokemon()
    for pkmn_name in pkmn_names:
        file.write("%s - %s\n" % (pkmn_name, scrape_description(pkmn_name)))

main()