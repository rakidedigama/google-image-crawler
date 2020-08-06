import os
import json 
import requests # to sent GET requests
from bs4 import BeautifulSoup # to parse HTML
import pandas as pd
import argparse

# user can input a topic and a number
# download first n images from google image search

GOOGLE_IMAGE = \
    'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

# The User-Agent request header contains a characteristic string 
# that allows the network protocol peers to identify the application type, 
# operating system, and software version of the requesting software user agent.
# needed for google search
usr_agent = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}

parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str)
parser.add_argument('--save_folder', type = str)


args = parser.parse_args()
SAVE_FOLDER = args.save_folder

def main():
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)
    
    n_images = 100 # number of html tags to crawl until a true image url is found for search. 

    search_list = get_search_list(args.input_file)
    print(search_list.head())
    print("Total number of items : ", len(search_list))

    for i, item in search_list.iterrows():
        try:

            item_title = item['title']
            item_id    = str(int(item['asin']))

            img_url = get_image_url(item_title, n_images)
            print(i,"/",len(search_list), " >  product : ", item, ", url : ", img_url)

            download_image(item_id, img_url)
            

        except:
            print("Could not download image for item ", item_title)


def get_search_list(input_csv):
    df = pd.read_csv(input_csv)
    print(df.info())

    print(df.head())

    search_list = df[['asin','title']]
    return search_list



def download_image(image_name, image_url):

    response = requests.get(image_url)

    imagename = SAVE_FOLDER + '/' + image_name  + '.jpg'
    with open(imagename, 'wb') as file:
        file.write(response.content)

        
    

def get_image_url(data, n_images):
    # ask for user input
    #data = input('What are you looking for? ')
   
    #n_images = int(input('How many images do you want? '))

    #print('Start searching...')
    
    # get url query string
    searchurl = GOOGLE_IMAGE + 'q=' + data
    #print(searchurl)

    # request url, without usr_agent the permission gets denied
    response = requests.get(searchurl, headers=usr_agent)
    html = response.text

    # find all divs where class='rg_meta'
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.findAll('img', {'class': 'rg_i Q4LuWd'}, limit=n_images)
    #print("Number of entries found : ", len(results))
    img_url = []
 
    image_count = 0
    for result in results:
        image_count +=1        
        #print(result)
        try:
            img_url = result['data-src']
            
            if img_url is not None:
                #print(image_count," : " , img_url)             
                return img_url            
            break    
        except:
            pass
            #print(image_count, " : No data-src")
            


    print("Did not get image url for ", data)
    exit()
 

if __name__ == '__main__':
    main()
