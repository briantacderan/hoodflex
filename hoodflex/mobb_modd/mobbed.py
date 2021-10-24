from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

class Mobbed:
    def __init__(self, company_name, form, year):
        self.company_name = company_name
        self.form = form
        self.year = year
        
    def get_stash(self):
        engine = create_engine('sqlite:///temp.db', echo=False, 
                               connect_args={ 'check_same_thread': False })
        session = create_session(bind=engine, autocommit=False, 
                                 autoflush=True)
        df_array = []
        file_array = []
        table_titles = []
        
        df_titles = ['BALANCE', 'INCOME', 'OPERATIONS', 'EQUITY', 'CASH']
        
        for i in range(len(df_titles)):
            filename = f"./static/resources/data/{self.company_name.lower().split(' ')[0].split(',')[0]}-{self.year}-{self.form.lower()}-{df_titles[i].lower()[0:4]}.csv"
            try:
                df = pd.read_csv(filename)
            except:
                df = None
                continue
            if df is not None:
                df_array.append(df)
                file_array.append(filename)
                table_titles.append(df_titles[i].lower().title())
        for i in range(len(table_titles)):
            df_array[i].to_sql(table_titles[i],
                              con=engine, if_exists='replace')
        return [df_array, file_array, table_titles, engine, session]
