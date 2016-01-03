import pandas as pd
import numpy as np





def to_iotable(name, rounds=None):
    df = pd.read_csv(name + '/trade.csv')
    if rounds is None:
        rounds = [max(df['round'])]
    for round in rounds:
        table = df[df['round'] == round]
        table.drop(['round', 'index'], axis=1, inplace=True)
        grouped_table = table.groupby(['seller', 'buyer'])
        quantities = grouped_table.sum()['quantity']
        prices = grouped_table.mean()['price']
        quantities = quantities.unstack()
        quantities = quantities.reindex_axis(['brd', 'mlk', 'tools', 'household', 'investment', 'netexport'], axis=0)
        quantities = quantities.reindex_axis(['brd', 'mlk', 'tools', 'household', 'investment', 'netexport'], axis=1)
        quantities = quantities.replace(np.NaN, 0)
        prices = prices.unstack()
        prices = prices.reindex_axis(['brd', 'mlk', 'tools', 'household', 'investment', 'netexport'], axis=0)
        prices = prices.reindex_axis(['brd', 'mlk', 'tools', 'household', 'investment', 'netexport'], axis=1)
        prices = prices.replace(np.NaN, 0)
        print '***\tquantities\t***'
        print quantities
        print '***\tprice\t***'
        print prices
        return quantities









if __name__ == '__main__':
    table = to_iotable('./result/cce_2016-01-03_10-19/')
