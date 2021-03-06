# -*- coding: utf-8 -*-

from google.colab import drive

drive.mount("/content/drive")

#!pip install selenium tqdm requests pillow
#!apt-get update 
#!apt install chromium-chromedriver
#!pip install webp

from selenium import webdriver
import urllib
import os
import time
import numpy as np
from tqdm import tqdm
import io
import requests
from PIL import Image

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def list_folds_to_complete(food_path):

  food_list=os.listdir(food_path)

  empty_folders=[]
  for j in range(len(food_list)):
    if not os.listdir(food_path+"/"+food_list[j]):
      empty_folders.append(food_list[j])

  for i in range(len(food_list)):
    food_list[i]=food_list[i].replace("_"," ")

  for i in range(len(empty_folders)):
    empty_folders[i]=empty_folders[i].replace("_"," ")

  return empty_folders



def rmv_emp_folds(food_path,emp_folds):

  for folder in emp_folds:
    folder=folder.replace(" ","_")
    os.rmdir(food_path+"/"+folder)

def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int):
    
    
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)    
        
    # build the google query
    search_url = "http://www.google.com/search?q={q}&tbm=isch"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = []
    image_count = 0
    results_start = 0
    last_height=0
    
    while image_count < max_links_to_fetch:
        
        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.append(actual_image.get_attribute('src'))              
                    image_count +=1     
                    if image_count == max_links_to_fetch:
                        print(f"Found: {len(image_urls)} image links, done!")
                        return image_urls 
         
        scroll_to_end(wd)
        new_height = wd.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            try:
                    load_more_button = wd.find_element_by_css_selector(".mye4qd")
                    time.sleep(2)
                    wd.execute_script("document.querySelector('.mye4qd').click();")
                    print("Loading more images..")
            
            except:
                    print("You arrived at the end of the page...")
                    return image_urls 
        else:
       
            last_height = new_height
            

        # move the result startpoint further down
        results_start = len(thumbnail_results)


    return image_urls

def save_images(links,path_folder,data_name,max_images):
    
    data_name=data_name.replace(" ","_")
    file_path=path_folder+"/"+data_name+"_"

    #vertical image
    min_ratio=4/5
    #horizontal image
    max_ratio=16/9
  
    #list composed of element=[image,image_dimension]
    saved_list=[]
  
    #remove duplicated links
    links= list(dict.fromkeys(links))

    for link in links:
           try:
                image_content = requests.get(link).content
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert('RGB')
                width, height = image.size
                ratio=width/height
                if ratio>=min_ratio and ratio<=max_ratio
                    saved_list.append([image,width*height])
           except:
                continue
    
    # descending sorting according to image dimension width*height
    saved_list=sorted(saved_list,key=lambda saved_list:saved_list[1], reverse=True)
    
    pbar = tqdm(total=max_images)
  
    #save the first max_images° images
    for i in range(max_images):
            name =file_path+str(i)+".jpeg"
            with open(name, 'wb') as f:
                    saved_list[i][0].save(f, "JPEG", quality=95)   
            f.close()
            pbar.update(1)
    pbar.close()

def search_and_download(search_term:str,wd_driver,target_path,number_images=50):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    print("Getting links..")
    with wd_driver as wd:
        res = fetch_image_urls(search_term, number_images*15, wd=wd, sleep_between_interactions=0.15)
        
    print("Getting images..")
    time.sleep(1)
    save_images(res,target_folder,search_term,number_images*3)

cnt=0
for food in empty_folders:
  cnt+=1
  print("Collecting "+str(cnt)+"° class of food :"+str(food))
  WD_DRIVER = webdriver.Chrome('chromedriver',options=chrome_options)
  search_and_download(food, WD_DRIVER)
