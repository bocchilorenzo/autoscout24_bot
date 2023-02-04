from requests import request
from bs4 import BeautifulSoup
from re import sub


def scrape(url, last_id, domain):
    """
    Scrape the given url and extract all the listings

    :param url: Url to scrape
    :param last_id: ID of the last listing from the previously scraped results
    :param domain: Domain of the website
    :return: True if the previous id was found (for pagination) and an array of car listings
    """
    res = request('get', url, headers={
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/109.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                  'Accept-Encoding': 'gzip, deflate, br'
                  }
                  )
    res.encoding = 'UTF-8'
    if res.ok:
        soup = BeautifulSoup(res.text, 'lxml')
        listings = soup.find_all("article")
        to_return = []
        found_previous_id = False
        website = url.split("/")[2]

        for listing in listings:
            all_paragraphs = listing.find_all('p')
            all_spans = listing.find_all('span')

            if domain in {"be", "en"}:
                price = ".".join(all_paragraphs[0].string.split("€")[1].split(","))[:-2].lstrip()
            else:
                price = sub(r"\s+", '.', all_paragraphs[0].string.split("€")[1].split(",")[0].lstrip())

            if domain in {"at", "fr", "pl", "cz", "hu", "ru", "bg", "se", "ua"}:
                kilometers = sub(r"\s+", '.', all_spans[1].string, 1)
            else:
                kilometers = all_spans[1].string
            
            if listing.get('id') != last_id:
                auto = {
                    'id': listing.get('id'),
                    'title': listing.find('h2').contents[0] + " " + (listing.find('h2').next_sibling.string if listing.find('h2').next_sibling.string else ""),
                    'price_euro': price,
                    'classification': all_paragraphs[1].string if len(all_paragraphs) > 1 else "-",
                    'kilometers': kilometers,
                    'year': all_spans[2].string,
                    'horsepower': all_spans[3].string,
                    'condition': all_spans[4].string,
                    'owners': all_spans[5].string,
                    'shift': all_spans[6].string,
                    'fuel': all_spans[7].string,
                    'fuel_consumption': all_spans[8].string,
                    'co2': all_spans[9].string,
                    'seller_type': all_spans[10].contents[0],
                    'seller_location': all_spans[-1].string if all_spans[-1].string else "-",
                    'url': "https://" + website + listing.find('a').get('href')
                }
                #auto['image'] = "".join(listing.find('img').get('src').rsplit("/")[:-1]) if listing.find('img') and len(next(listing.find('div').children).contents) > 0 else "-"
                to_return.append(auto)
            else:
                found_previous_id = True
                break
        return found_previous_id, to_return
    else:
        raise Exception("Error while scraping")
