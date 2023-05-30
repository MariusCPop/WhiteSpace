import datetime
import requests
import bs4
import xlsxwriter
import json

#this is the main menu to select area and maximum price

with open('cartier.json', 'r') as f:
    data = json.load(f)

# Extract the options for the specified area
print("Optiunile de cartier sunt urmatoarele:")
for cartier in data:
    print(cartier['number']+ ") " + cartier['cartier'])

# Ask the user to select an option
selection = input('Selecteaza un cartier din optiunile de mai sus: ')

# Convert the user input to an integer and subtract 1 to get the index of the selected option
index = int(selection) - 1
optiunea = data[index]["number"]
cartierul = data[index]["cartier"]

pret_maxim = input('Introduceti pretul maxim in euro: ')

# Print the selected option
print(f'Ati selectat optiunea {optiunea}, cartierul {cartierul} cu un pret maxim de {pret_maxim} euro')



# This is the base url to which parameters are added
# area = 'baciu'
area = cartierul.lower()
base_url = 'https://www.piata-az.ro/imobiliare/apartamente-de-vanzare/cluj-napoca/'+area

# These are the filtering paramenters to streamline the search process
query_params = {
    # 'price_to': '100000',
    'price_to': f'{pret_maxim}',
    'paymethod': 'price'
}

#The scraping starts at page one and it keeps going to the next page as long as there are results
page_num = 1
ads = []

while True:
    url = base_url + f'?page={page_num}'
    response = requests.get(url, params=query_params)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    new_ads = soup.find_all('div', class_='announcement announcement--pf')
    if not new_ads:
        break
    ads += new_ads
    page_num += 1

# print(ads)
print('Number of ads found:', len(ads)) # add this line to check number of ads

apartments = []

for ad in ads:
    name = ad.find('a', class_='announcement__description__title')['title']
    price = ad.find('div', class_='announcement__info__price').text

    #the price will be split in value and currency using the /n separator
    detailed_price = price.split('\n')

    link = ad.find('a')['href']
    apartment = {'name': name, 'price_value': detailed_price[1], 'price_currency': detailed_price[2], 'link': "https://www.piata-az.ro"+link}
    apartments.append(apartment)

for apartment in apartments:
    print(apartment)

# The results will be added to an excel file to have a log
workbook = xlsxwriter.Workbook(f'{area}{datetime.datetime.now().date()}.xlsx')
worksheet = workbook.add_worksheet(f"{datetime.datetime.now().date()}")

row = 0
col = 0
worksheet.write(row, col, 'Nume')
worksheet.write(row, col + 1, 'Pret')
worksheet.write(row, col + 2, 'Valuta')
worksheet.write(row, col + 3, 'Link')
row += 1

for apartament in apartments:
    try:
        if float(apartament['price_value']):
            worksheet.write(row, col, apartament['name'])
            worksheet.write(row, col + 1, apartament['price_value'])
            worksheet.write(row, col + 2, apartament['price_currency'])
            worksheet.write(row, col + 3, apartament['link'])
            row += 1
    except ValueError:
        continue
workbook.close()

input("Press Enter to exit...")

"""
Ideas to go forward:
1. Create executable file with dynamic location and max price - almost done
2. Create menu with options for location based on exterior txt file - done
"""
