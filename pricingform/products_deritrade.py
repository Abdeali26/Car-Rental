from rest_framework import serializers
from rest_framework.exceptions import APIException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from collections import OrderedDict
import datetime
import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys          


class ProductCommonFeatures(object):
    """contains functions for common parameters in products"""
    
    def __init__(self, arg):
        super(ProductCommonFeatures, self).__init__()
        self.arg = arg

    def login(self, product_no):
        driver = webdriver.Chrome()
        # url is set for the desired product number
        urls = 'https://www.deritrade.com/en-GB/PrimaryMarket/PricingForm?productType=' + product_no
        final_result = {}
        outfile = open('out_file.csv', 'w')
        
        product = urls[58:]
        driver.get(urls)
        try:
            assert "Login" in driver.title
        except Exception as e:
            raise APIException ("Assertion Error")
        user = driver.find_element_by_name("USERNAME")
        user.clear()
        print ("Logging In....")
        user.send_keys("antonio.denegri@cirdancapital.com")
        password = driver.find_element_by_name("PASSWORD")
        password.clear()
        password.send_keys("wUrRu6Q$k`32n={9")                  

        driver.find_element_by_id("submit-button").click()
        try:
            print ("Wait Until Starts")
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "formHd"))
            )
            print element
            print ("Wait Until Completed")
        except:
            print ("Error in wait until")

        try:
            assert "Create A New Product" in driver.title
        except Exception as e:
            raise APIException ("Assertion Error")
        time.sleep(5)
        return urls, driver, product, final_result, outfile
    
    def set_intital_fix_date(self, driver, validated_data):
        initial_fixing_date = driver.find_element_by_name('InitialFixingDate')
        initial_fixing_date.clear()
        initial_fixing_date.click()
        time.sleep(1)
        initial_fixing_date.send_keys(validated_data['InitialFixing'][0])

    def set_final_fix_date(self, driver, validated_data):
        final_fixing_date = driver.find_element_by_name('FinalFixingDate')
        final_fixing_date.clear()
        final_fixing_date.click()
        final_fixing_date.send_keys(validated_data['FinalFixing'][0])

    def set_underlying(self, driver, validated_data, product):
        for val in validated_data['UnderLying'][product]:                   
            underlying = driver.find_element_by_id("inputUnderlyingAutoComplete")
            underlying.send_keys(val)
            time.sleep(12)
            underlying.send_keys(Keys.DOWN);
            underlying.send_keys(Keys.RETURN);
            # suggestion = driver.find_element_by_css_selector(".underlyingAutoComplete li").click()

    def set_solve_for_value(self, driver, validated_data):
        solve_for = Select(driver.find_element_by_id('SolveFor'))
        solve_for.select_by_visible_text(validated_data['SolveFor'][0])
        if solve_for.first_selected_option.text == 'Coupon':
            strike = driver.find_element_by_name('Strike')
            strike.clear()
            strike.send_keys(validated_data['Strike'][0])
        else:
            driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][0])
    
    def get_common_parameters(self, result, html_head):
        result['Product Type'] = html_head.find_all('td')[0].get_text()[13:]
        result['Investment Amount'] = html_head.find_all('td')[1].get_text()[18:]
        result['Commission'] = html_head.find_all('td')[2].get_text()[11:]
        result['Request ID / Time'] = html_head.find_all('td')[3].get_text()[18:]
        result['Trade | Payment'] = html_head.find_all('td')[4].get_text()[16:]
        result['Term'] = html_head.find_all('td')[5].get_text()[5:]
        result['Final Fixing | Redemption'] = html_head.find_all('td')[6].get_text()[26:]

        


def product_type_41(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    # Signing in to the website.
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try: # Injecting the form paramters.
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(2)
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            time.sleep(2)
            
            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)                   
            product_common_feature_obj.set_underlying(driver, validated_data, product)            
            product_common_feature_obj.set_solve_for_value(driver, validated_data)            
            
            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])


            time.sleep(2) # Submitting the form.
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)
            # Exception raised if selenium unable to locate html elements.

        # Below code fetches html from the result page.
        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}
        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        if val.get_text() == "Delta":
                            break
                        result['values'][_][val.get_text()] = ''
                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        if ind > 2:
                            break
                        item[list(result['values'][0])[ind]] = row.get_text()   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)
        # Raises exception when error occures in fetching results for this product.
    
    # Output is written to csv file
    outfile.write(str(final_result))
    return final_result



def product_type_12(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(2)
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            time.sleep(2)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)                   
            
            driver.find_element_by_name('Barrier').send_keys(validated_data['Barrier'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])
            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            solve_for = Select(driver.find_element_by_id('SolveFor'))
            solve_for.select_by_visible_text(validated_data['SolveFor'][count])
            if solve_for.first_selected_option.text == 'Coupon':
                strike = driver.find_element_by_name('Strike')
                strike.clear()
                strike.send_keys(validated_data['Strike'][count])
            else:
                driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result


def product_type_1(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(2)
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            time.sleep(2)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)                   
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  
            
            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])
            driver.find_element_by_name('Barrier').send_keys(validated_data['Barrier'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])
            
            solve_for = Select(driver.find_element_by_id('SolveFor'))
            solve_for.select_by_visible_text(validated_data['SolveFor'][count])
            if solve_for.first_selected_option.text == 'Coupon':
                strike = driver.find_element_by_name('Strike')
                strike.clear()
                strike.send_keys(validated_data['Strike'][count])
            else:
                driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        if val.get_text() == "Delta":
                            break
                        result['values'][_][val.get_text()] = ''
                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        if ind > 3 :
                            break
                        item[list(result['values'][0])[ind]] = row.get_text()   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result




def product_type_38(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(2)
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            time.sleep(2)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])
            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('EarlyRedemption').send_keys(validated_data['AutocallLevel'][count])
            driver.find_element_by_name('FinalFixingTenors').send_keys(validated_data['Tenor'][count])
            driver.find_element_by_name('GuaranteedCoupons').send_keys(validated_data['FirstObservationIn'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])

            solve_for = Select(driver.find_element_by_id('SolveFor'))
            solve_for.select_by_visible_text(validated_data['SolveFor'][count])
            if solve_for.first_selected_option.text == 'Coupon':
                strike = driver.find_element_by_name('Strike')
                strike.clear()
                strike.send_keys(validated_data['Strike'][count])
            else:
                driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string+ "  " +data.find(class_='secondary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result



def product_type_21(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(5)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  
                                
            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])
            driver.find_element_by_name('Barrier').send_keys(validated_data['Barrier'][count])               
            driver.find_element_by_name('PiecesUI').send_keys(validated_data['EnterTrade'][count])
            driver.find_element_by_name('Cap').send_keys(validated_data['Cap'][count])
            driver.find_element_by_name('Ratio').send_keys(validated_data['Ratio'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-7")
                table2 = data.find("table", class_="col-sm-5")
                result['Strike'] = data.find(class_='primary').string+ "  " +data.find(class_='secondary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                    result['values'][_][table2.find_all('th')[0].get_text()] = ''

                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()
                    for ind, row in enumerate(table2.find_all('tr')[index+1].find_all('td')):
                        flag = 4
                        item[list(result['values'][0])[flag]] = row.get_text()
                        break

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result



def product_type_6(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(5)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)                  
            product_common_feature_obj.set_underlying(driver, validated_data, product)

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])
            driver.find_element_by_name('AmountUI').send_keys(validated_data['EnterTrade'][count])
            driver.find_element_by_name('Floor').send_keys(validated_data['Floor'][count])
            
            strike = driver.find_element_by_name('Strike')
            strike.clear()
            strike.send_keys(validated_data['Strike'][count])
            
            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            result['Participation'] = data.find("span", class_="primary").get_text()
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                # import pdb;pdb.set_trace()
                table = data.find("table", class_="col-sm-7")
                table2 = data.find("table", class_="col-sm-5")
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                    result['values'][_][table2.find_all('th')[0].get_text()] = ''

                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()
                    for ind, row in enumerate(table2.find_all('tr')[index+1].find_all('td')):
                        flag = 4
                        item[list(result['values'][0])[flag]] = row.get_text()
                        break

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result        



def product_type_7(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")          
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(5)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])
            driver.find_element_by_name('AmountUI').send_keys(validated_data['EnterTrade'][count])
            driver.find_element_by_name('Floor').send_keys(validated_data['Floor'][count])
            driver.find_element_by_name('Participation').send_keys(validated_data['Participation'][count])

            strike = driver.find_element_by_name('Strike')
            strike.clear()
            strike.send_keys(validated_data['Strike'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click() 
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            result['Cap'] = data.find(class_='primary').string+ "  " +data.find(class_='secondary').string
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-7")
                table2 = data.find("table", class_="col-sm-5")
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                    flag = 1
                    for val in table2.find_all('th'):
                        if flag > 2 :
                            break
                        result['values'][_][val.get_text()] = ''
                        flag = flag + 1

                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()
                    flag = 4
                    for ind, row in enumerate(table2.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[flag]] = row.get_text()
                        flag = flag + 1
                        if flag > 5:
                            break

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result



def product_type_37(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])
            
            time.sleep(2)
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            time.sleep(2)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('Barrier').send_keys(validated_data['Barrier'][count])
            driver.find_element_by_name('EarlyRedemption').send_keys(validated_data['AutocallLevel'][count])
            driver.find_element_by_name('FinalFixingTenors').send_keys(validated_data['Tenor'][count])
            driver.find_element_by_name('GuaranteedCoupons').send_keys(validated_data['FirstObservationIn'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])

            solve_for = Select(driver.find_element_by_id('SolveFor'))
            solve_for.select_by_visible_text(validated_data['SolveFor'][count])
            if solve_for.first_selected_option.text == 'Coupon':
                strike = driver.find_element_by_name('Strike')
                strike.clear()
                strike.send_keys(validated_data['Strike'][count])
            else:
                driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][count])
            
            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string+ "  " +data.find(class_='secondary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result

def product_type_40(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])
            time.sleep(5)
            try :        
                driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            except :
                pass
            time.sleep(5)

            # **Intial date is already filled in this form and is uneditable**
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])
            driver.find_element_by_name('Barrier').send_keys(validated_data['Barrier'][count])
            driver.find_element_by_name('EarlyRedemption').send_keys(validated_data['AutocallLevel'][count])
            driver.find_element_by_name('FinalFixingTenors').send_keys(validated_data['Tenor'][count])
            driver.find_element_by_name('GuaranteedCoupons').send_keys(validated_data['FirstObservationIn'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])

            solve_for = Select(driver.find_element_by_id('SolveFor'))
            solve_for.select_by_visible_text(validated_data['SolveFor'][count])
            if solve_for.first_selected_option.text == 'Coupon':
                strike = driver.find_element_by_name('Strike')
                strike.clear()
                strike.send_keys(validated_data['Strike'][count])
            else:
                driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result


def product_type_42(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(2)
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            time.sleep(2)

            # **Intial date is already filled in this form and is uneditable**
            
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('EarlyRedemption').send_keys(validated_data['AutocallLevel'][count])
            driver.find_element_by_name('FinalFixingTenors').send_keys(validated_data['Tenor'][count])
            driver.find_element_by_name('GuaranteedCoupons').send_keys(validated_data['FirstObservationIn'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])

            solve_for = Select(driver.find_element_by_id('SolveFor'))
            solve_for.select_by_visible_text(validated_data['SolveFor'][count])
            if solve_for.first_selected_option.text == 'Coupon':
                strike = driver.find_element_by_name('Strike')
                strike.clear()
                strike.send_keys(validated_data['Strike'][count])
            else:
                driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string+ "  " +data.find(class_='secondary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result


def product_type_2(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])

            time.sleep(2)
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count]) 
            time.sleep(2)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])

            solve_for = Select(driver.find_element_by_id('SolveFor'))
            solve_for.select_by_visible_text(validated_data['SolveFor'][count])
            if solve_for.first_selected_option.text == 'Coupon':
                strike = driver.find_element_by_name('Strike')
                strike.clear()
                strike.send_keys(validated_data['Strike'][count])
            else:
                driver.find_element_by_name('Coupon').send_keys(validated_data['Coupon'][count])

            Select(driver.find_element_by_name('CouponFrequency')).select_by_visible_text(validated_data['Frequency'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-10")
                result['COUPON P.A'] = data.find(class_='primary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    flag = 1;
                    for val in table.find_all('th'):
                        if flag > 3:
                            break
                        result['values'][_][val.get_text()] = ''
                        flag = flag + 1
                for index,item in enumerate(result['values']):
                    flag = 1;
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        if flag > 3:
                            break
                        item[list(result['values'][0])[ind]] = row.get_text()
                        flag = flag + 1   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result


def product_type_10(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])
            
            time.sleep(2)
            driver.find_element_by_id('inputPieces').send_keys(validated_data['EnterTrade'][count]) 
            time.sleep(2)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('FinalFixingDate').send_keys(validated_data['FinalFixing'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)
            result['Factor'] = head.find_all('td')[7].get_text()[7:]        
            
        if soup.find("div", class_='responseBd'): 
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-7")
                table2 = data.find("table", class_="col-sm-5")
                result['Cap'] = str(data.find("span", class_="primary").get_text())+ "  " +str(data.find("span", class_="secondary").get_text())
                result['values'] = []
                rows = len(table.find_all('tr')) - 1   

                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                    for val in table2.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                        break

                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()
                    for ind, row in enumerate(table2.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[3]] = row.get_text()
                        break

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result


def product_type_4(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])
            Select(driver.find_element_by_name('TradeDropdown')).select_by_visible_text(validated_data['ProductTradedIn'][count])
            time.sleep(5)
            
            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  

            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])
            driver.find_element_by_id('inputAmount').send_keys(validated_data['Amount'][count])
            time.sleep(7)

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}
        # import pdb;pdb.set_trace()
        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-7")
                table2 = data.find("table", class_="col-sm-5")
                result['MAX YIELD P.A'] = str(data.find("span", class_="primary").get_text())+ "  " +str(data.find("span", class_="secondary").get_text())
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                    for val in table2.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                        break

                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()
                    for ind, row in enumerate(table2.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[3]] = row.get_text()
                        break

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result



def product_type_8(validated_data, product_no):
    product_common_feature_obj = ProductCommonFeatures(object)
    url, driver, product, final_result, outfile = product_common_feature_obj.login(product_no)
    count = 0
    try:
        try:
            print ("Injecting form params....")                 
            Select(driver.find_element_by_name('ClientDomicile')).select_by_visible_text(validated_data['Domicile'][count])
            Select(driver.find_element_by_name('SettlementType')).select_by_visible_text(validated_data['Settlement'][count])
            Select(driver.find_element_by_id('selCurrencyList')).select_by_visible_text(validated_data['Currency'][count])
            time.sleep(5)

            product_common_feature_obj.set_intital_fix_date(driver, validated_data)
            product_common_feature_obj.set_final_fix_date(driver, validated_data)
            product_common_feature_obj.set_underlying(driver, validated_data, product)                  
            
            Select(driver.find_element_by_id('PointOfTime')).select_by_visible_text(validated_data['TimeType'][count])
            Select(driver.find_element_by_name('Listing')).select_by_visible_text(validated_data['Listing'][count])                 
            driver.find_element_by_name('PiecesUI').send_keys(validated_data['EnterTrade'][count])
            driver.find_element_by_name('Barrier').send_keys(validated_data['Barrier'][count])
            driver.find_element_by_name('Ratio').send_keys(validated_data['Ratio'][count])
            driver.find_element_by_name('SalesCredit').send_keys(validated_data['Commission'][count])
            
            ratio = driver.find_element_by_name('Ratio')
            ratio.clear()
            ratio.click()
            ratio.send_keys(validated_data['Ratio'][count]) 

            time.sleep(2)
            driver.find_element_by_name('submit').click()
        except Exception as e:
            raise (e)

        print ("Fetching result....")
        try:
            print ("wait until starts")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "col-sm-10"))
            ) 
            print ("wait until completed")     
        except Exception as e:
            print ("Error in wait until")
                  

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}

        if soup.find("div", class_='responseHd'):
            head = soup.find("div", class_="responseHd")
            product_common_feature_obj.get_common_parameters(result, head)        

        if soup.find("div", class_='responseBd'):
            data = soup.find("div", class_="responseBd")
            try:
                error = data.find("div", class_="errorMessage")
                result['error'] = error.get_text()
            except:
                table = data.find("table", class_="col-sm-7")
                table2 = data.find("table", class_="col-sm-5")
                result['Strike'] = data.find(class_='primary').string+ "  " +data.find(class_='secondary').string
                result['values'] = []
                rows = len(table.find_all('tr')) - 1                
                for _ in range(rows):
                    result['values'].append(OrderedDict())
                    for val in table.find_all('th'):
                        result['values'][_][val.get_text()] = ''
                    result['values'][_][table2.find_all('th')[0].get_text()] = ''

                for index,item in enumerate(result['values']):
                    for ind, row in enumerate(table.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[ind]] = row.get_text()
                    for ind, row in enumerate(table2.find_all('tr')[index+1].find_all('td')):
                        item[list(result['values'][0])[3]] = row.get_text()
                        break   

        if soup.find("div", class_='formErrorBd'):
            result['error'] = soup.find("div", class_='formErrorBd').get_text()
        final_result[product] = result
    except Exception as e:
        raise (e)

    outfile.write(str(final_result))
    return final_result