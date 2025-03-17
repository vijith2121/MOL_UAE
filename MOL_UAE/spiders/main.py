import scrapy
from MOL_UAE.items import Product
from lxml import html
import json
import copy

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
            # 'Cookie': 'ASP.NET_SessionId=ncbcomwoadn1ldkm3nipjobq; ADRUM_BTa=R:0|g:8ee13b72-5606-413c-95c1-08ce6ba377a6|n:mohre_0a9b3c27-4648-4b8d-9c9c-591021814a68; SameSite=None; ADRUM_BT1=R:0|i:28664|e:95',
        }

        json_data = {
            'pageNumber': 1,
            'pageSize': 10,
            'name': '',
            'labourCardNo': '81982017',
            'passportNo': '',
        }
        url = 'https://mobilebeta.mohre.gov.ae/Mohre.Complaints.App/TwafouqAnonymous/GetPersonList'
        yield scrapy.Request(
            url,
            headers=headers,
            # json=json_data,
            body=json.dumps(json_data),
            callback=self.parse_product,
            method='POST',
        )

    def parse_product(self, response):
        product_data = response.json()
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
            # 'Cookie': 'ASP.NET_SessionId=ncbcomwoadn1ldkm3nipjobq; ADRUM_BTa=R:78|g:e37cb677-5e5c-4e30-baef-5ad16cb2ae7e|n:mohre_0a9b3c27-4648-4b8d-9c9c-591021814a68; SameSite=None; ADRUM_BT1=R:78|i:28664|e:42; PersonCode=11816018303154',
        }

        json_data = {
            'pageNumber': 1,
            'pageSize': 10,
            'personCode': '11816018303154',
        }
        for item in product_data:
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
        product_data = response.json()[0]
        meta_data = response.meta
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
        }
        yield Product(**items)