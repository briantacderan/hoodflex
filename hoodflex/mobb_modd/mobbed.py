from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from hoodflex.mobb_modd._slapper import GoodLook

class Mobbed(GoodLook):
    def __init__(self, company_name, form, year, **kwargs):
        super().__init__(**kwargs)
        self.company_name = company_name
        self.form = form
        self.year = year
        
    def complete_scrape(self, csv=False, df_title='RAND', titles=['N/A'], statements={'N/A': 'VOID'}):
        try:
            maybe = False
            for i in range(len(self.titles)):
                title_split = self.titles[i].upper().split(' ')
                for j in range(len(title_split)):
                    if title_split[j] == df_title:
                        index_maybe = i
                        maybe = True
                    if title_split[j][1:4] == 'PAR' \
                    and j == len(title_split) - 1:
                        maybe = False
                    elif title_split[j][1:4] != 'PAR' \
                    and j == len(title_split) - 1 and maybe == True:
                        maybe = False
                        index = index_maybe
            statement_name = titles[index]
            df = statements[statement_name]
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
        except:
            return [None, None]
        
    def get_stash(self, df_array, table_titles):
        engine = create_engine('sqlite:///temp.db', echo=False, 
                               connect_args={ 'check_same_thread': False })
        session = create_session(bind=engine, autocommit=False, autoflush=True)
        
        for i in range(len(table_titles)):
            df_array[i].to_sql(table_titles[i], con=engine, if_exists='replace')
        return [engine, session]
