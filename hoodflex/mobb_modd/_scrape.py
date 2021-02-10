import pandas as pd
import requests
import datetime as dt
from bs4 import BeautifulSoup

today = dt.datetime.now()
year = str(today.year)
month = '0' + str(today.month) if today.month < 10 else str(today.month)
day = '0' + str(today.day) if today.day < 10 else str(today.day)
current_date = year + month + day

class EdgaRequesta:
    def __init__(self, company_name, form, year, date=current_date, edgar_url='https://www.sec.gov/Archives/edgar/data', edgar_ep='https://www.sec.gov/cgi-bin/browse-edgar', sec_url='https://www.sec.gov'):
        self.company_name = company_name
        self.form = form
        self.year = year
        self.date = date
        self.edgar_url = edgar_url
        self.edgar_ep = edgar_ep
        self.sec_url = sec_url
        
    def company_soup(self, xml):
        output = 'atom' if xml else ''
        parser = 'lxml' if xml else 'html.parser'
        param_dict = {'action': 'getcompany',
                      'dateb': self.date,
                      'owner': 'exclude',
                      'output': output,
                      'company': self.company_name}
        webpage_response = requests.get(url=self.edgar_ep, params=param_dict)
        soup = BeautifulSoup(webpage_response.content, parser)
        return soup
    
    def master_list(self):
        self.soup_html = self.company_soup(xml=False)
        doc_table = self.soup_html.find_all('table', class_='tableFile2')

        master_list = []

        for row in doc_table[0].find_all('tr'):
            cols = row.find_all('td')

            if len(cols) != 0:
                filing_type = cols[0].text.strip()                 
                filing_date = cols[3].text.strip()
                filing_numb = cols[4].text.strip()

                filing_doc_href = cols[1].find('a', {'href': True, 'id': 'documentsbutton'})
                filing_int_href = cols[1].find('a', {'href': True, 'id': 'interactiveDataBtn'})
                filing_num_href = cols[4].find('a')

                if filing_doc_href != None:
                    filing_doc_link = self.sec_url + filing_doc_href['href'] 
                else:
                    filing_doc_link = 'no link'

                if filing_int_href != None:
                    filing_int_link = self.sec_url + filing_int_href['href'] 
                else:
                    filing_int_link = 'no link'

                if filing_num_href != None:
                    filing_num_link = self.sec_url + filing_num_href['href'] 
                else:
                    filing_num_link = 'no link'

                file_dict = {}

                file_dict['file_type'] = filing_type
                file_dict['file_number'] = filing_numb
                file_dict['file_date'] = filing_date
                
                file_dict['links'] = {}

                file_dict['links']['documents'] = filing_doc_link
                file_dict['links']['interactive_data'] = filing_int_link
                file_dict['links']['filing_number'] = filing_num_link

                master_list.append(file_dict)
        return master_list
    
    def master_list_xml(self):
        entries = self.soup_xml.find_all('entry')

        master_list_xml = []

        for entry in entries:
            accession_num = entry.find('accession-number').text

            entry_dict = {}
            entry_dict[accession_num] = {}

            category_info = entry.find('category')

            entry_dict[accession_num]['category'] = {}
            
            entry_dict[accession_num]['category']['label'] = category_info['label']
            entry_dict[accession_num]['category']['scheme'] = category_info['scheme']
            entry_dict[accession_num]['category']['term'] =  category_info['term']

            entry_dict[accession_num]['file_info'] = {}
            
            if entry.find('act') != None:
                entry_dict[accession_num]['file_info']['act'] = entry.find('act').text
            if entry.find('file-number') != None:
                entry_dict[accession_num]['file_info']['file_number'] = entry.find('file-number').text
            if entry.find('file-number-href') != None:
                entry_dict[accession_num]['file_info']['file_number_href'] = entry.find('file-number-href').text
            if entry.find('filing-date') != None:
                entry_dict[accession_num]['file_info']['filing_date'] =  entry.find('filing-date').text
            if entry.find('filing-href') != None:
                entry_dict[accession_num]['file_info']['filing_href'] = entry.find('filing-href').text
            if entry.find('filing-type') != None:
                entry_dict[accession_num]['file_info']['filing_type'] =  entry.find('filing-type').text
            if entry.find('film-number') != None:
                entry_dict[accession_num]['file_info']['form_number'] =  entry.find('film-number').text
            if entry.find('form-name') != None:
                entry_dict[accession_num]['file_info']['form_name'] =  entry.find('form-name').text
            if entry.find('size') != None:
                entry_dict[accession_num]['file_info']['file_size'] =  entry.find('size').text

            entry_dict[accession_num]['request_info'] = {}
            
            entry_dict[accession_num]['request_info']['link'] =  entry.find('link')['href']
            entry_dict[accession_num]['request_info']['title'] =  entry.find('title').text
            entry_dict[accession_num]['request_info']['last_updated'] =  entry.find('updated').text

            master_list_xml.append(entry_dict)
        return master_list_xml
    
    def recent_form_index(self):
        self.ml_html = self.master_list()
        title_length = len(self.form)
        for i in range(len(self.ml_html)):
            if self.ml_html[i]['file_type'][0:title_length] == self.form:
                recent_form_index = i
                break
        return recent_form_index
    
    def xml_help(self):
        self.soup_xml = self.company_soup(xml=True)
        ml_index = self.recent_form_index()
        entries = self.soup_xml.find_all('entry')
        self.ml_xml = self.master_list_xml()
        
        xml_help = []

        xml_access_num = entries[ml_index].find('accession-number').text
        xml_help.append({'access_num': xml_access_num})
        
        xml_category = self.ml_xml[ml_index][entries[ml_index]\
                           .find('accession-number').text]['category']
        for key, value in xml_category.items():
            xml_help.append({key: value})

        xml_info = self.ml_xml[ml_index][entries[ml_index]
                       .find('accession-number').text]['file_info']
        for key, value in xml_info.items():
            xml_help.append({key: value})

        xml_requests = self.ml_xml[ml_index][entries[ml_index]\
                           .find('accession-number').text]['request_info']
        for key, value in xml_requests.items():
            xml_help.append({key: value})

        return xml_help
    
    def master_form_list(self):
        xml_help = self.xml_help()
        
        column_list = []
        value_list = []

        for each in xml_help:
            key, value = list(each.items())[0]
            column_list.append(key)
            value_list.append(value)
        master_form_list = pd.DataFrame(columns=column_list)
        master_form_list.loc[0] = value_list
        master_form_list.set_index('form_number', inplace=True)

        return master_form_list
    
    def cik(self):
        self.mf_list = self.master_form_list()
        filing_href = self.mf_list['filing_href']
        cik_num = filing_href[0].split('/')[-3]
        return cik_num
    
    def filing_summary_url(self):
        cik_num = self.cik()
        access_num = self.mf_list.access_num[0]
        access_num = ''.join(access_num.split('-'))
        components = [cik_num, access_num, 'index.json']
        filing_url = self.make_url(components)
        content = requests.get(filing_url)
        document_content = content.json()
        for document in document_content['directory']['item']:
            if document['type'] != 'image2.gif':
                doc_name = document['name']
                if doc_name == 'FilingSummary.xml':
                    comp = [cik_num, access_num, doc_name]
                    doc_url = self.make_url(comp)
        return doc_url
    
    def master_reports(self):
        doc_url = self.filing_summary_url()
        content = requests.get(doc_url).content
        soup = BeautifulSoup(content, 'lxml')
        reports = soup.find('myreports')
        company_base_url = doc_url.replace('FilingSummary.xml', '')
        
        master_reports = []
        
        for report in reports.find_all('report')[:-1]:
            report_dict = {}
            report_dict['name_short'] = report.shortname.text
            report_dict['name_long'] = report.longname.text
            report_dict['position'] = report.position.text
            report_dict['category'] = report.menucategory.text
            report_dict['url'] = company_base_url + report.htmlfilename.text
            master_reports.append(report_dict)
            
        return master_reports
    
    def consolidated_reports(self):
        reports = self.master_reports()
        reports_list = []
        
        for report in reports:
            if report['category'] == 'Statements':
                reports_list.append(report)
                
        return reports_list
    
    def statements_urls(self):
        consolidated = self.consolidated_reports()
        statements_urls = []
        
        for report in consolidated:
            statement_url = report['url']
            statements_urls.append(statement_url)
            
        return statements_urls
    
    def statements_names(self):
        consolidated = self.consolidated_reports()
        statements_names = []

        for report in consolidated:
            statement_name = report['name_short']
            statements_names.append(statement_name)

        return statements_names

    def statements_info(self):
        consolidated = self.consolidated_reports()
        statements_names = []
        statements_urls = []
        for report in consolidated:
            statement_name = report['name_short']
            statements_names.append(statement_name)
            statement_url = report['url']
            statements_urls.append(statement_url)

        return [statements_urls, statements_names]
    
    def make_url(self, comp):
        url = self.edgar_url
        for r in comp:
            url = '{}/{}'.format(url, r)
        return url