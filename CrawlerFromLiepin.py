# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 15:40:02 2018

@author: ice
"""



import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

class CrawlerFromLiepin():
    """
    该项目只针对猎聘网站招聘信息的爬取
    使用方法：
        在猎聘网站请先选好招聘的地点
        选择需要的行业
        最后在搜索栏输入关键字
        将得到的网址作为url
    """
    
    def __init__(self, url, page):
        """
        url:str 网址
        page:int 爬取多少个页面
        """
        self.url = url
        self.page = page
        
        
    def get_all_info(self):
        """
        爬去猎聘网站上的招聘信息
        url:str 猎聘网址
        page：int 需要爬取网页页数
        """
        
        def get_details(net):
            """
            爬取单个招聘信息
            爬取的信息如下
            公司名称、所在区与、职位名称、发布日期、工资待遇、聘用资格、公司福利（标签）
            """
            result = {}
            res = requests.get(net)
            soup = BeautifulSoup(res.text, "html.parser")

            result["company"] = soup.select(".title-info h3")[0].text.strip() #公司名称
            result["zone"] = soup.select(".basic-infor span")[0].text.strip() #公司所在区
            result["position"] = soup.select(".title-info h1")[0].text.strip() #职位名称
            result["release_date"] = soup.select(".basic-infor time")[0]["title"] #发布日期
            result["salary"] = soup.select(".job-title-left p")[0].text.strip() #工资待遇
   
            #聘用资格 由于部分网页使用class名称不一样加上本人水平有限，故写了两个for循环来爬取该信息
            result["qualifications"] = []                               
            for qualification in soup.select(".resume.clearfix span"):
                result["qualifications"].append(qualification.text)
    
            for qualification in soup.select(".job-qualifications span"):
                result["qualifications"].append(qualification.text)

            #公司福利（标签）       
            result["labels"] = []
            for label in soup.select(".comp-tag-box span"):
                result["labels"].append(label.text)
    
            #职位描述
            result["context"] = soup.select(".content.content-word")[0].text.strip()
    
            return result


        def get_one_page_info(p_url):
            """
            爬取单个页面上的所有招聘信息
            """
            p_res = requests.get(p_url)
            p_soup = BeautifulSoup(p_res.text, "html.parser")
    
            #页面上每一个招聘信息的url有区别，故提取出完整的url放置在nets列表里
            nets = []
            for i in p_soup.select(".job-info"):
                head = "https://www.liepin.com" 
                body = i.a["href"]+"?"+i.a["data-promid"]
                if head not in body:
                    body = head + body
                    nets.append(body)  
        
            #由于部分招聘页面所用的标签名称，格式有区别，
            #不能用之前编写好的函数爬取（主要原因是本人能力有限TOT），
            #故放弃该网址的爬取，将其url打印出来单独查看
            res = []
            for net in nets:
                try:
                    res.append(get_details(net))
                except IndexError:
                    print("该网页不能爬取，请单独查看")
                    print(net)
    
            return res

        #现在爬取所有页面信息并放入total列表
        url = self.url[:-1] + "{}" #将页面的页码格式化
        total = [] 
        print("Crawling now, wait a moment,please!")
        
        for page in range(self.page):
            
            one_page = get_one_page_info(url.format(page))
            total.extend(one_page)
            print("page", page+1, "is done")
            
        return total

    
    def save_info(self, total, name=""):
        """
        将爬取的信息保存成excel格式
        total: list 爬取信息的列表
        name: str 保存的文件名
        """
    
        dataframe = pd.DataFrame(total)
        today = datetime.datetime.strftime(datetime.date.today(), "%Y%m%d") #当天的日期
        file_name = today + name + ".xlsx"
        dataframe.to_excel(file_name)
        print("Saved!")
        
        return file_name
    
