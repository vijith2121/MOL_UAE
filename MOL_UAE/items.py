import scrapy


class Product(scrapy.Item):
    passport_no = scrapy.Field()
    cif = scrapy.Field()
    emirates_id = scrapy.Field()
    nameAr = scrapy.Field()
    nameEn = scrapy.Field()
    gender = scrapy.Field()          # Added gender field
    nationality = scrapy.Field()
    personCode = scrapy.Field()
    dateofbirth = scrapy.Field()     # Use the same naming as in your dict
    companyCode = scrapy.Field()
    CompanynameEn = scrapy.Field()   # Use the same naming as in your dict
    CompanynameAr = scrapy.Field()
    lastCardNo = scrapy.Field()
    cardStartDate = scrapy.Field()
    cardEndDate = scrapy.Field()
    cardType = scrapy.Field()
    extra_data = scrapy.Field()