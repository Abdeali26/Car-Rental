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
from seleniumlogin import force_login
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ProductCommonFeatures(object):
    """Class for ProductCommonFeatures"""

    def __init__(self, arg):
        super(ProductCommonFeatures, self).__init__()
        self.driver = webdriver.Chrome()
        self.url = "https://sp.sgmarkets.com"

    def login(self):
        self.driver.get(self.url)
        try:
            element = WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.ID, "UserName"))
            )
        except Exception as e:
            pass

        email = self.driver.find_element_by_id("UserName")
        email.clear()
        email.click()
        email.send_keys("marco.oprandi@cirdancapital.com")

        passowrd = self.driver.find_element_by_id("pw-wrapper")
        passowrd.clear()
        passowrd.click()
        passowrd.send_keys("061291Joint!")

        self.driver.find_element_by_id("btn-login").click()

        # try:
        #     element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME,"tfa-button-submit")))
        # except Exception as e:
        #     pass

        # self.driver.find_element_by_css_selector(".tfa-button-submit").click()
    
    def set_product(self, value):
        prod_div = self.driver.find_element_by_id("ProductType")
        p_div = prod_div.find_element_by_tag_name("div")
        if value == "Autocall":
            p_div.click()
            div_p = p_div.find_element_by_css_selector('.dropdown-menu li:nth-of-type(1)').click()
        else:
            p_div.click()
            div_p = p_div.find_element_by_css_selector('.dropdown-menu li:nth-of-type(2)').click()
        
    def set_product_subtype(self, value):
        ps = self.driver.find_element_by_id("$ctrl_request_$ctrl_data_id_1")
        Select(ps).select_by_visible_text(value)

    def set_mautrity_value(self, value):
        mv = self.driver.find_element_by_css_selector("[placeholder='Maturity Value']")
        mv.click()
        time.sleep(1)
        mv.clear()
        mv.send_keys(value)

    def set_solve_for(self, value):
        sf = self.driver.find_element_by_css_selector("[placeholder='Solve For']")
        Select(sf).select_by_visible_text(value)

    def set_currency(self, value):
        currency = self.driver.find_element_by_css_selector("[placeholder='Currency']")
        Select(currency).select_by_visible_text(value)

    def set_notional_amt(self, value):
        namt = self.driver.find_element_by_id("ezFormField6")
        namt.click()
        time.sleep(1)
        namt.clear()
        namt.send_keys(value)

    def set_remuneration_mode(self, value):
        rm = self.driver.find_element_by_css_selector("[placeholder='Remuneration Mode']")
        Select(rm).select_by_visible_text(value)

    def set_upfront_fee(self, value):
        ufee = self.driver.find_element_by_id("$ctrl_value8")
        ufee.click()
        time.sleep(1)
        ufee.clear()
        ufee.send_keys(value) 

    def set_settlement_type(self, value):
        st = self.driver.find_element_by_css_selector("[placeholder='Settlement Type']")
        Select(st).select_by_visible_text(value)

    def set_strike(self, value):
        strike_span = self.driver.find_element_by_id("Strike")
        strike = strike_span.find_element_by_id("$ctrl_value8")
        strike.click()
        time.sleep(1)
        strike.clear()
        strike.send_keys(value)

    def set_barrier_type(self, value):
        b_type = self.driver.find_element_by_css_selector("[placeholder='Barrier Type']")
        Select(b_type).select_by_visible_text(value)

    def set_ki_barrier(self, value):
        kib_span = self.driver.find_element_by_id("KiBarrier")
        ki_b = kib_span.find_element_by_id("$ctrl_value8")
        ki_b.click()
        time.sleep(1)
        ki_b.clear()
        ki_b.send_keys(value)

    def set_recall_start_at_period(self, value):
        rsap = self.driver.find_element_by_css_selector("[placeholder='Recall Start At Period']")
        Select(rsap).select_by_visible_text(value)

    def set_observation_frequency(self, value):
        rsap = self.driver.find_element_by_css_selector("[placeholder='Observation Frequency']")
        Select(rsap).select_by_visible_text(value)

    def set_coupon_barrier(self, value):
        cb_span = self.driver.find_element_by_id("CouponBarrier")
        cb_div = cb_span.find_element_by_class_name("combo-box")
        cb = cb_div.find_element_by_class_name("form-control")
        cb.click()
        time.sleep(1)
        cb.clear()
        cb.send_keys(value)

    def set_coupon_definition_type(self, value):
        cb_div = self.driver.find_element_by_id("CouponDefType")
        c_div = cb_div.find_element_by_id("$ctrl_request_$ctrl_data_id_1")
        c_div.click()
        time.sleep(1)
        c_div.send_keys(value) 

    def set_underlying(self, values):
        for value in values : 
            time.sleep(4)
            under_div = self.driver.find_element_by_id("Underlying")
            u_div = under_div.find_element_by_id("$ctrl_currentUnderlying3")
            u_div.send_keys(value)
            time.sleep(4)
            u_div.send_keys(Keys.DOWN);
            u_div.send_keys(Keys.RETURN);

    def set_recall_threshold(self, value):
        rt_span = self.driver.find_element_by_id("RecallThreshold")
        rt_div = rt_span.find_element_by_class_name("combo-box")
        rt = rt_div.find_element_by_class_name("form-control")
        rt.click()
        time.sleep(1)
        rt.clear()
        rt.send_keys(value)

    def submit_indicative_quote(self):
        iq_div = self.driver.find_element_by_id("quote-panel")
        q_div = iq_div.find_element_by_class_name("col-xs-6")
        q_div.click()
        time.sleep(1)

    def start_new_quote(self):
        rsap = self.driver.find_element_by_css_selector("[title='Add a new tab']")
        rsap.click()

    def wait_till_call_authentication(self):
        try:
            print ("Waiting for call authentication")
            element = WebDriverWait(self.driver, 3000).until(
                EC.presence_of_element_located((By.ID, "ProductType"))
            )
        except:
            print ("Error in wait until")

    def get_result(self):
        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        result = {}
        if soup.find("div", class_='QP-product-list-container'):
            head = soup.find("div", class_='QP-product-list-container')
            dt_length = len(head.find_all('dt'))
            for index in range(dt_length):
                result[head.find_all('dt')[index].get_text()] = head.find_all('dd')[index].get_text()

        return result
        


def automate_sgmarkets_forms(validated_data):
    pcf = ProductCommonFeatures(object)
    pcf.login()
    pcf.wait_till_call_authentication()
    time.sleep(15)
    outfile = open('out_file.csv', 'w')
    final_result = { }
    no_of_products = len(validated_data["ProductID"])
    for list_index in range(no_of_products):
        pcf.start_new_quote()
        time.sleep(4)
        pcf.set_product(validated_data["Product"][list_index])
        time.sleep(3)
        pcf.set_product_subtype(validated_data["ProductSubtype"][list_index])
        time.sleep(2)
        pcf.set_mautrity_value(validated_data["MaturityValue"][list_index])
        pcf.set_solve_for(validated_data["SolveFor"][list_index])
        pcf.set_currency(validated_data["Currency"][list_index])
        pcf.set_notional_amt(validated_data["NotionalAmount"][list_index])
        pcf.set_remuneration_mode(validated_data["RemunerationMode"][list_index])
        pcf.set_upfront_fee(validated_data["UpfrontFee"][list_index])
        pcf.set_settlement_type(validated_data["SettlementType"][list_index])
        pcf.set_strike(validated_data["Strike"][list_index])
        pcf.set_observation_frequency(validated_data["ObservationFrequency"][list_index])
        pcf.set_underlying(validated_data["UnderLying"][list_index])
        time.sleep(2)
        if validated_data["ProductID"][list_index] != "5":
            pcf.set_barrier_type(validated_data["BarrierType"][list_index])
            pcf.set_ki_barrier(validated_data["KIBarrier"][list_index])
        if validated_data["ProductID"][list_index] != "5": 
            if validated_data["ProductID"][list_index] != "6":
                pcf.set_recall_start_at_period(validated_data["RecallStartAtPeriod"][list_index])
                time.sleep(4)
                pcf.set_recall_threshold(validated_data["RecallThreshold"][list_index])
        if validated_data["ProductID"][list_index] == "2" or validated_data["ProductID"][list_index] == "3":
            pcf.set_coupon_barrier(validated_data["CouponBarrier"][list_index])
        if validated_data["ProductID"][list_index] == "5" or validated_data["ProductID"][list_index] == "6":
            pcf.set_coupon_definition_type(validated_data["CouponDefinitionType"][list_index])
        
        pcf.submit_indicative_quote()
        time.sleep(60)
        result = pcf.get_result()

        product = (validated_data["ProductSubtype"][list_index]).upper()
        final_result[product] = result
        # Write data into csv file
        outfile.write(str(final_result))
    
    return final_result
