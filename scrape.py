import requests
from bs4 import BeautifulSoup
import json
import sys

###### SCRAPER ######
def clean_text(txt: str) -> str:
    """Replace all white space with single space."""
    return " ".join(txt.strip().split())

def parse_rows(rows):
    split_rows = [row.split("  ") for row in rows]
    split_split_rows = []
    for row in split_rows:
        list_strs = []
        for str in row:
            if str != '' and str!= " ":
                list_strs.append(str)     
        split_split_rows.append(list_strs)
    return split_split_rows

def scrape(url: str) -> 'tuple[list[str], list[str]]':
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup("h1")[0].text

    ingr_class = "ingredients-item-name"
    ingr_tags = soup("span", class_=ingr_class)
    ingredients = [clean_text(ingr.text) for ingr in ingr_tags]

    instr_class = "subcontainer instructions-section-item"
    instr_tags = soup("li", class_=instr_class)
    instructions = [clean_text(instr.div.div.p.text) for instr in instr_tags]
    
    return title, ingredients, instructions

def scrape_ingr_subs(url: str):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    table_row_class = "tableRow"
    table_rows = soup("tr", class_=table_row_class)
    table_rows_content = []
    count = 0 
    for table_row in table_rows: 
        table_rows_content.append(table_row.text)

    rows = parse_rows(table_rows_content)

    sub_dict = {}
    for row in rows[1:-1]:
        sub_dict[row[0]] = {}
        sub_dict[row[0]]["amount"] = row[1]
        sub_dict[row[0]]["substitution"] = row[2]
    
    f = open("subs.json", "w")
    json.dump(sub_dict, f)
    f.close()
    return sub_dict






#url = "https://www.allrecipes.com/article/common-ingredient-substitutions/"


