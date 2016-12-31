from lxml import html
import pickle
import codecs
import requests
import re

def scrape_description(pkmn_name):
    pkmn_name = pkmn_name.replace(u'\xe9','e').replace(u'\u2640','-f').replace(u'\u2642','-m')
    pkmn_name = pkmn_name.replace(': ','-').replace(' ','-').replace('\'','').replace('.','')
    print(pkmn_name)
    page = requests.get('http://pokemondb.net/pokedex/' + pkmn_name)
    tree = html.fromstring(page.content)
    dex_entry = tree.xpath('/html/body/article/table/tbody/tr[2]/td/text()')
    return dex_entry[0]

def scrape_pokemon(option):
    #page = requests.get('http://www.serebii.net/sunmoon/alolapokedex.shtml')
    page = requests.get('http://www.serebii.net/pokedex-sm/')
    tree = html.fromstring(page.content)
    #list = tree.xpath('//a[contains(@href,\'/pokedex-sm/\')]/text()')
    list = tree.xpath('//form[contains(@name,\''+option+'\')]/select/option[contains(@value,\'/pokedex-sm/\')]/text()')
    cleaned_list = []
    for x in list:
        re.sub("[^a-zA-z0-9!@#,/.,#!$%^&*;:{}=-_`~( )/]+", "", x)
        cleaned_list.extend(x.splitlines())
        #cleaned_list.extend(re.findall(r'([A-Z,-])\w', x))
    return cleaned_list

def main():
    description_file = codecs.open('descriptions.txt', 'w', 'utf-8')
    pkmn_names = scrape_pokemon('wibble')
    pkmn_names.extend(scrape_pokemon('orna'))
    pkmn_names.extend(scrape_pokemon('mounty'))
    for pkmn_name in pkmn_names:
        description_file.write("%s\n" % (scrape_description(pkmn_name)))
    with open('names.txt', 'wb') as f:
        pickle.dump(pkmn_names, f)

main()