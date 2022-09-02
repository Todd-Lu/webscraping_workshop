import time
import random
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas as pd

import os
my_cwd = 'C:\\Users\\toddj\\Documents\\GitHub\\webscraping_workshop'
os.chdir(my_cwd)

# the following script accesses the NLRB Website, filters cases so we only look at Unfair Labor Practice Filings, collects meta-data into a spreadsheet
# Beginning link: https://www.nlrb.gov/reports/graphs-data/recent-filings?page=0



output_df_filename = 'data\\nlrb_output.csv'
nlrb_url = 'https://www.nlrb.gov/reports/graphs-data/recent-filings?page=0'
driver = webdriver.Chrome()
driver.get(nlrb_url) #access the web page


# Filter the search

    # find the ULP check mark, then click it
ulp_check = driver.find_element_by_css_selector('#panel_case_type > form > fieldset > div:nth-child(3) > label')
ulp_check.click()
    
    # set items per page to 100, not 20 (which is default)
items_per_page = Select(driver.find_element_by_css_selector('#edit-number'))                                    
items_per_page.select_by_visible_text(str(100))
                                                     
    # click "apply"
apply_button = driver.find_element_by_css_selector('#edit-submit')
apply_button.click()                                                   


# set up function that collects what we want from the page

def nlrb_page_to_csv(driver):
        
        #get list of charged party
    charged_elemlist = driver.find_elements_by_css_selector('#nlrb_cases_main h3')
    charged_list = []  
    
    for element in charged_elemlist:
        charged_list.append(element.text)
    
        #get list of url links to court cases                                                    
    casenum_elemlist = driver.find_elements_by_css_selector('.rer-style-1 a')
    casenum_links_list = []
    
    for element in casenum_elemlist:
        casenum_links_list.append(element.get_attribute('href'))
    
        #get metadata for all texts                                                    
    metadata_elemlist = driver.find_elements_by_css_selector('.rer-style-1')
    metadata_list = []
    
    for element in metadata_elemlist:
        metadata_list.append(element.text)
    
    md_dict = {"case_num" : metadata_list[::6],
               "date_filed" : metadata_list[1::6],
               "status" : metadata_list[2::6],
               "num_employees" : metadata_list[3::6],
               "location" : metadata_list[4::6],
               "nlrb_region" :metadata_list[5::6]}
    
        #for column in dictionary, remove part of string
    for index in range(0, len(md_dict["case_num"])):
        md_dict["case_num"][index] = md_dict["case_num"][index].replace('Case Number: ', '')
        md_dict['date_filed'][index] = md_dict['date_filed'][index].replace('Date Filed: ', '')
        md_dict['status'][index] = md_dict['status'][index].replace('Status: ', '')
        md_dict['num_employees'][index] = md_dict['num_employees'][index].replace('No Employees: ', '')
        md_dict['location'][index] = md_dict['location'][index].replace('Location: ', '')
        md_dict['nlrb_region'][index] = md_dict['nlrb_region'][index].replace('Region Assigned: ', '')
    md_dict['case_url'] = casenum_links_list
    md_dict['charged_party'] = charged_list
    out_df = pd.DataFrame.from_dict(md_dict)
    
    return out_df

begin_page = 0
end_page = 5

for page_num in range(0, end_page + 1):
    
    print('Accessing page: ', str(page_num + 1))
    output_df = nlrb_page_to_csv(driver)
    
    if not os.path.exists(output_df_filename):
        output_df.to_csv(output_df_filename, index = False, encoding ='utf-8')
        
    else:
        output_df.to_csv(output_df_filename,
                         mode = 'a',
                         header = False,
                         index = False,
                         encoding = 'utf-8')
        
    next_page_button = driver.find_elements_by_css_selector('.pager__item--next span')[1]
    next_page_button.click()
    print('Finished scraping page. Now pausing before going to next page')    
    time.sleep(random.uniform(2.5, 7))


driver.close()