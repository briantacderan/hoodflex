import numpy as np
import pandas as pd
import requests
import re
import urllib
from bs4 import BeautifulSoup

from hoodflex.mobb_modd._scrape import EdgaRequesta

class SecuritySpider(EdgaRequesta):
    def __init__(self, company_name, form, year, **kwargs):
        super().__init__(company_name, form, year, **kwargs)
        self.urls_list, self.statements_names = self.statements_info()
        
    def convert_statement(self, index):
        statement_url = self.urls_list[index]
        content = requests.get(statement_url).content
        soup = BeautifulSoup(content, 'html.parser')

        statement_data = {}
        statement_data['headers'] = []
        statement_data['sections'] = []
        statement_data['data'] = []

        count_a = 0
        count_b = 0
        codes_list_a = []
        codes_list_b = []
        displacement = 0
        sec_index = []

        for index, row in enumerate(soup.table.find_all('tr')):

            cols = row.find_all('td')
            th_rows = row.find_all('th')
            st_rows = row.find_all('strong')
            pl = row.find_all(attrs={'class': 'pl'})
            year = 0

            # if it's a regular row and not a section or a table header
            if len(th_rows) == 0 and len(st_rows) == 0:
                ex = str(cols)
                reg_row = [ele.text.strip().split(', ')[0].split(' - ')[0].split(':')[0] for ele in cols]
                if 'defref_srt_ProductOrServiceAxis=us-gaap_' in ex:
                    sec_row = cols[0].text.strip().split(':')[0]
                    statement_data['sections'].append(sec_row)
                    sec_index.append(index-displacement)
                    displacement += 1
                    count_a += 1
                else:
                    if not statement_data['data']:
                        if not statement_data['sections']:
                            statement_data['sections'].append(first_section_header)
                            sec_index.append(index-displacement)
                    statement_data['data'].append(reg_row)
                    if pl:
                        codes_list_a.append(count_a)
                        codes_list_b.append(count_b)
                        count_b += 1

            # if it's a regular row and a section but not a table header
            elif len(th_rows) == 0 and len(st_rows) != 0:
                sec_row = cols[0].text.strip().split(':')[0]
                statement_data['sections'].append(sec_row)
                sec_index.append(index-displacement)
                displacement += 1
                if len(statement_data['data']) > 0:
                    count_a += 1

            # finally if it's not any of those it must be a header
            elif len(th_rows) != 0:
                hed_row = [ele.text.strip().split(':')[0] for ele in th_rows]
                statement_data['headers'].append(hed_row)
                displacement += 1
                if index == 0:
                    first_section_header = hed_row[0]

        if len(statement_data['headers']) > 1:
            columns_list = statement_data['headers'][1]
        else:
            columns_list = statement_data['headers'][0][1:]
        sections_list = statement_data['sections']
        accounts_list = [row[0] for row in statement_data['data']]

        columns_delete = []
        for i in range(len(columns_list)):
            if columns_list[i] == None or columns_list[i] == '' or columns_list[i][0] == '[':
                columns_delete.append(i)
        columns_delete.sort(reverse=True)
        for index in columns_delete:
            columns_list.pop(index)
        num_columns = len(columns_list)

        delete_index = [0]
        for i in range(len(statement_data['data'][0])-1):
            for j in range(count_b):
                if statement_data['data'][j][i+1]:
                    if statement_data['data'][j][i+1][0] == '[':
                        delete_index.append(i+1)
        delete_index = list(dict.fromkeys(delete_index))
        delete_index.sort(reverse=True)
        for i in range(count_b):
            for index in delete_index:
                statement_data['data'][i].pop(index)
        data_list = statement_data['data'][:count_b]

        name_list = [sections_list, accounts_list, columns_list]

        for i in range(len(name_list)):
            new_list = []
            for each in name_list[i]:
                if each in new_list:
                    new_each = each + ' ||'
                    while new_each in new_list:
                        new_each = new_each + '|'
                    new_list.append(new_each)
                else:
                    new_list.append(each)
            if name_list[i] == accounts_list:
                name_list[i] = new_list[:count_b]
            else:
                name_list[i] = new_list

        midx = pd.MultiIndex(levels=[name_list[0],
                                     name_list[1]],
                             codes=[codes_list_a,
                                    codes_list_b], 
                             names=['category', 'account'])
        df = pd.DataFrame(index=midx, columns=name_list[2],
                          data=data_list)

        df = df.replace('[\$,)]','', regex=True )\
               .replace('[(]','-', regex=True)\
               .replace('', 0, regex=True)

        try:
            df = df.astype(float)
        except:
            pass

        return df
    
    def statements_dictionary(self):
        statements = {}

        for i in range(len(self.statements_names)):
            df = self.convert_statement(i)
            statements[self.statements_names[i]] = df

        return statements
    
    def statements_titles(self):
        statements = self.statements_dictionary()
        statements_titles = list(statements.keys())
        return statements_titles
    
    def dictionary_info(self):
        statements = self.statements_dictionary()
        statements_titles = list(statements.keys())
        return [statements, statements_titles]
