from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from hoodflex.mobb_modd._slapper import GoodLook

class Mobbin(GoodLook):
    def __init__(self, company_name, form, year, **kwargs):
        super().__init__(company_name, form, year, **kwargs)
        self.statements, self.titles = self.dictionary_info()
        
        """
        ----------------------------------------------------------------
        ----------------------------------------------------------------
        -----                                                      -----
        -                    $$$$$$ hoodflex $$$$$$                    -
        -                              X                               -
        -                    $$$$$$$ mobbin $$$$$$$                    -
        -----                                                      -----
        ----------------------------------------------------------------
        ----------------------------------------------------------------
        
        
                                  ----------
                                  Parameters
                                  ----------
        
        
        company_name : string
        
            --full company name i.e. 'Ideanomics, Inc.'
            --preferrably as shown on EDGAR SEC company search
        
        form : string
        
            --3-4 character length, regardless of actual length
            --i.e. '10-Q', '10-K', '424A', '8-K'
            --preferably as shown on EDGAR SEC company/form search
            
        year : string
        
            --format: '2020'
        
                      **** optional keyword arguments ****

        date : string
        
            --format: 'YYYYMMDD'
            --input custom date if you want EDGAR to search files only
              before that date
              
            
        --------------------------------
            
                           (modules in development)
        
        RECOMMENDATION: (1) For the time being, if failing to scrape EDGAR 
                        data, go through methods on this list in order,
                        to see where module fails to parse data. It is 
                        free to edit where you see fit. 
                        
                        (2) Most likely will succeed at scraping company
                        statements, rather than forms of descriptions
                        
                            <<UPDATE COMING SOON>>
                          
        --------------------------------
        
        
                                --------------
                                Usable Methods
                                --------------
        
        
            EdgaRequesta:
            ------------

        .company_soup(xml)                              -- xml : Boolean
        
            --finds Beautiful Soup webpage response
            --set XML as true for 'lxml' parser, false for 'html.parser' 
            
        .master_list()
        
        .master_list_xml()
        
        .recent_form_index()
        
        .xml_help()
        
        .master_form_list()
        
        .cik()
        
        .filing_summary_url()
        
        .master_reports()
        
        .consolidated_reports()
        
        .statements_urls()
        
        .statements_names()
        
        
            SecuritySpider:
            ---------------
               **web scrape from EdgaRequesta must be complete**
            
        .convert_statement(index)                     -- index : Integer
        
        .statements_dictionary()
        
        .statements_titles()
        
        
            GoodLook:
            ---------
                 **can use for stylying any pandas DataFrame**
            
        .style_negative
        
        .conditional_formatter(df)
        
        .bold_border
            
            
                         ----------------------------
                         Dependent Modules & Packages
                         ----------------------------
        
        import pandas as pd
        import numpy as np

        import requests
        import re
        import urllib
        from bs4 import BeautifulSoup
        import datetime as dt
        
        
        
        ----------------------------------------------------------------
        
        ----------------------------------------------------------------
        ----------------------------------------------------------------
        """ 
        
    def __repr__(self):
        line1 = '\n\n\n\nStatement Titles:\n\n\n' + '-'*100 + '\n\n'
        line_titles = ''
        for i in range(len(self.titles)):
            line_titles += f'\n       Statement Index: {i} - ' + self.titles[i]
        last = '\n\n\n' + '-'*100 + '\n\n\n\n\n\n\n'
        return f'{line1}{line_titles}{last}'
        
    def complete_scrape(self, csv=False, df_title='RAND'):
        maybe = False
        for i in range(len(self.titles)):
            title_split = self.titles[i].upper().split(' ')
            for j in range(len(title_split)):
                if title_split[j] == df_title:
                    index_maybe = i
                    maybe = True
                if title_split[j][1:4] == 'PAR' and j == len(title_split) - 1:
                    maybe = False
                elif title_split[j][1:4] != 'PAR' and j == len(title_split) - 1 and maybe == True:
                    maybe = False
                    index = index_maybe
        statement_name = self.titles[index]
        df = self.statements[statement_name]
        filename = None
        if csv:
            filename = f"./static/resources/data/{self.company_name.lower().split(' ')[0].split(',')[0]}-{self.year}-{self.form.lower()}-{df_title[0:4].lower()}.csv"
            df.to_csv(filename)
        df_copy = df.copy()
        df_styled = self.style_table(df_copy, statement_name)
        if filename:
            return [df, filename]
        else:    
            return [df, df_styled]
            
    def statements_to_csv(self, df_titles=['BALANCE', 'INCOME', 'OPERATIONS', 'EQUITY', 'CASH']):
        df_array = []
        file_array = []
        for i in range(len(df_titles)):
            df, file = self.complete_scrape(csv=True, df_title=df_titles[i])
            df_array.append(df)
            file_array.append(file)
        return [df_array, file_array]
    
    def statements_to_sql(self):
        self.df_array, self.file_array = self.statements_to_csv()
        engine = create_engine('sqlite:///temp.db', echo=False)
        session = create_session(bind=engine, autocommit=False, autoflush=True)
        self.df_array[0].to_sql('Balance', con=engine, if_exists='replace')
        self.df_array[1].to_sql('Income', con=engine, if_exists='replace')
        self.df_array[2].to_sql('Operation', con=engine, if_exists='replace')
        self.df_array[3].to_sql('Equity', con=engine, if_exists='replace')
        self.df_array[4].to_sql('Cash', con=engine, if_exists='replace')
        return [self.df_array, self.file_array, engine, session]
