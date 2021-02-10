from hoodflex.mobb_modd._hustle import SecuritySpider

class GoodLook(SecuritySpider):
    def __init__(self, company_name, form, year, **kwargs):
        super().__init__(company_name, form, year, **kwargs)
        
    def style_negative(self, value):
        if type(value) == str:
            color = 'red' if value[0] == '(' else 'black'
            return 'color: %s' % color

    def conditional_formatter(self, df):
        col_num = len(df.columns)
        index_list = list(df.index)
        k = 0
        for i in range(len(df.index)):
            x = index_list[i][1]
            for j in range(col_num):
                val = float(df.iloc[i, j])
                val = int(val)
                df.iloc[i, j] = val
                if val < 0:
                    abs_val = -val
                    df.iloc[i, j] = '({0:,.0f})'.format(abs_val)
                    continue
                if x[0:5] == 'Total' or x[0:5] == 'Gross' or x[0:11] == 'Loss before' or x[0:9] == 'Loss from' or x[0:8] == 'Net loss' or x[0:8] == 'Net cash' or x[0:12] == 'Net increase':
                    df.iloc[i, j] = '${0:,.0f}'.format(val)
                    k += 1
                    if k <= 2:
                        df.iloc[0, j] = '${0:,.0f}'.format(val)
                else:
                    df.iloc[i, j] = '{0:,.0f}'.format(val)
        return df

    def bold_border(self, cell):
        return ['border-bottom: 1px black solid; font-weight: bold;'
                if cell.name[1][0:5] == 'Total' 
                or cell.name[1][0:5] == 'Gross' 
                or cell.name[1][0:11] == 'Loss before'
                or cell.name[1][0:9] == 'Loss from'
                or cell.name[1][0:8] == 'Net loss'
                or cell.name[1][0:8] == 'Net cash'
                or cell.name[1][0:12] == 'Net increase'
                else '' for i in cell]

    def style_table(self, df, statement_name):
        df_styled = self.conditional_formatter(df)
        df_styled = df.style.applymap(self.style_negative)\
                            .set_caption(self.form + ' - ' + statement_name + \
                                         ' - ' + self.company_name.upper())\
                            .apply(self.bold_border, axis=1)
        return df_styled
