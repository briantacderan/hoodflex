from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from hoodflex.mobb_modd._slapper import GoodLook

class Mobbed(GoodLook):
    def __init__(self, company_name, form, year, titles=['N/A'], statements={'N/A': 'VOID'}, **kwargs):
        super().__init__(**kwargs)
        self.company_name = company_name
        self.form = form
        self.year = year
        self.titles = titles
        self.statements = statements
        
    def complete_scrape(self, csv=False, df_title='RAND'):
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
        except: 
            return [None, None]
        
    def get_stash(self):
        df_array = []
        file_array = []
        table_titles = []
        
        df_titles = ['BALANCE', 'INCOME', 'OPERATIONS', 'EQUITY', 'CASH']
        
        for i in range(len(df_titles)):
            filename = f"./static/resources/data/{self.company_name.lower().split(' ')[0].split(',')[0]}-{self.year}-{self.form.lower()}-{df_titles[i][0:4].lower()}.csv"
            print(f'Attempt to get file: \n{filename}\n.\n..\n....\n........\n')
            try:
                df = pd.read_csv(filename)
                print(f'DataFrame {df_titles[i]} fetch succeeded\n')
            except:
                df = None
                print('No DataFrame available\n')
                continue
            if df is not None:
                print('Creating assets: df_array, file_array, and table_titles\n')
                df_array.append(df)
                file_array.append(filename)
                table_titles.append(df_titles[i].lower().title())
                
        print(f'Total length of available statements: {len(table_titles)}\n')
         
        engine = create_engine('sqlite:///temp.db', echo=False, 
                               connect_args={ 'check_same_thread': False })
        session = create_session(bind=engine, autocommit=False, autoflush=True)
        for i in range(len(table_titles)):
            df_array[i].to_sql(table_titles[i], con=engine, if_exists='replace')
        return [df_array, file_array, table_titles, engine, session]
