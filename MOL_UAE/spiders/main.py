import scrapy
from MOL_UAE.items import Product
from lxml import html
import json
import copy
from datetime import datetime
import os
import pandas as pd

class Mol_uaeSpider(scrapy.Spider):
    name = "MOL_UAE"
    start_urls = ["https://example.com"]

    def parse(self, response):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://mobilebeta.mohre.gov.ae',
            'Referer': 'https://mobilebeta.mohre.gov.ae/Mohre.Complaints.App/TwafouqAnonymous/Employee',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'lang': '1',
            'sec-ch-ua': '"Not:A-Brand";v="24", "Chromium";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }

        json_data = {
            'pageNumber': 1,
            'pageSize': 20,
            'name': '',
            # 'labourCardNo': '81982017',
            'labourCardNo': '',
            'passportNo': 'F5110797',
        }
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, "split_part_13.csv")
        df = pd.read_csv(file_path)
        for item in df.to_dict('records'):
            passport_no = item.get('Passport No.').replace(' ', '').strip()
            cif = str(item.get('CIF', '')).replace(' ', '').strip()
            CIS_CID_No = str(item.get('CIS/CID No.')).replace(' ', '').strip()
            emirates_id = item.get('EID Number').replace(' ', '').replace('-', '').strip()
            json_data['passportNo'] = passport_no
            url = 'https://mobilebeta.mohre.gov.ae/Mohre.Complaints.App/TwafouqAnonymous/GetPersonList'
            input_data = {
                'passport_no': passport_no,
                'cif': cif,
                'emirates_id': emirates_id,
                'CIS_CID_No': CIS_CID_No
            }
            yield scrapy.Request(
                url,
                headers=headers,
                # json=json_data,
                meta = input_data,
                body=json.dumps(json_data),
                callback=self.parse_product,
                method='POST',
            )
            # return

    def parse_product(self, response):
        item = response.json()
        try:
            item = response.json()[0]
        except Exception as e:
            print(e)
            return
        meta_data = response.meta
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://mobilebeta.mohre.gov.ae',
            'Referer': 'https://mobilebeta.mohre.gov.ae/Mohre.Complaints.App/TwafouqAnonymous/PersonCompany?w=MTE4MTYwMTgzMDMxNTQ=&x=null',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'lang': '1',
            'sec-ch-ua': '"Not:A-Brand";v="24", "Chromium";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }

        json_data = {
            'pageNumber': 1,
            'pageSize': 10,
            'personCode': '11816018303154',
        }
        # for item in product_data_list:
        nameAr = item.get('nameAr', None)
        nameEn = item.get('nameEn', None)
        gender = item.get('gender', None)
        nationality = item.get('nationality', None)
        personCode = item.get('personCode', None)
        date_of_birth = item.get('dob', None)
        data = {
            'name_Ar': nameAr,
            'name_En': nameEn,
            'gender': gender,
            'nationality': nationality,
            'personCode': personCode,
            'date_of_birth': date_of_birth,
            'extra_data': response.json(),
            'passport_no': meta_data.get('passport_no', None),
            'cif': meta_data.get('cif', None),
            'emirates_id': meta_data.get('emirates_id', None),
            'CIS_CID_No': meta_data.get('CIS_CID_No', None)
        }
        api_url = 'https://mobilebeta.mohre.gov.ae/Mohre.Complaints.App/TwafouqAnonymous/GetPersonCompanies'
        json_data['personCode'] = f'{personCode}'
        yield scrapy.Request(
            api_url,
            headers=headers,
            meta=data,
            body=json.dumps(json_data),
            callback=self.parse_product_data,
            method='POST',

        )

    def parse_product_data(self, response):
        product_list = response.json()
        date_format = "%d/%m/%Y"
        valid_products = [p for p in product_list if p.get('cardStartDate')]
        
        if not valid_products:
            return []  # No valid dates found
        
        # Get the most recent date
        recent_date = max(valid_products, key=lambda x: datetime.strptime(x['cardStartDate'], date_format))['cardStartDate']
        
        # Collect records with the most recent date
        product_data = [p for p in valid_products if p['cardStartDate'] == recent_date][0]
        # product_data = response.json()[0]
        meta_data = response.meta
        extra_datas = meta_data.get('extra_data', [])
        if not isinstance(extra_datas, list):
            extra_datas = [extra_datas]
        extra_datas.extend(response.json())

        companyCode = product_data.get('companyCode', None)
        Company_name_En = product_data.get('nameEn', None)
        Company_name_Ar = product_data.get('nameAr', None)
        lastCardNo = product_data.get('lastCardNo', None)
        cardStartDate = product_data.get('cardStartDate', None)
        cardEndDate = product_data.get('cardEndDate', None)
        cardType = product_data.get('cardType', None)

        meta_data['companyCode'] = companyCode
        meta_data['Company_name_En'] = Company_name_En
        meta_data['Company_name_Ar'] = Company_name_Ar
        meta_data['lastCardNo'] = lastCardNo
        meta_data['cardStartDate'] = cardStartDate
        meta_data['cardEndDate'] = cardEndDate
        meta_data['cardType'] = cardType
        meta_data['extra_data'] = extra_datas
        meta_data.pop("depth", None)
        meta_data.pop("download_timeout", None)
        meta_data.pop("download_slot", None)
        meta_data.pop("download_latency", None)
        items = {
            'nameAr': ''.join(meta_data.get('name_Ar', '')).strip(),
            'nameEn': meta_data.get('name_En', None),
            'gender': meta_data.get('gender', None),
            'nationality': meta_data.get('nationality', None),
            'personCode': meta_data.get('personCode', None),
            'dateofbirth': meta_data.get('date_of_birth', None),
            'companyCode': companyCode,
            'CompanynameEn': Company_name_En,
            'CompanynameAr': Company_name_Ar,
            'lastCardNo': lastCardNo,
            'cardStartDate': cardStartDate,
            'cardEndDate': cardEndDate,
            'cardType': cardType,
            'extra_data': extra_datas,
            'passport_no': meta_data.get('passport_no', None),
            'cif': meta_data.get('cif', None),
            'emirates_id': meta_data.get('emirates_id', None),
            'CIS_CID_No': meta_data.get('CIS_CID_No', None)
        }
        yield Product(**items)