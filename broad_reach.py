import pandas as pd
file_location = '/Users/samuelbodansky/PnL_Task/Task data.xlsx'
df = pd.read_excel(file_location)
df.columns = df.iloc[0]
df = df[1:]
df1 = df.loc[:,df.columns.notnull()]
trade_table = df1.iloc[:,0:4].dropna()
instrument_table = df1.iloc[:,4:8].dropna()
contract_table = df1.iloc[:,8:12].dropna()
eod_table = df1.iloc[:,12:29].dropna()
fx_table = df1.iloc[:,29:].dropna()

contract_and_instrument = contract_table.merge(instrument_table)
print('please enter date in format YYYY-MM-DD')
user_input = input()
print('PnL Description')
test_date = pd.to_datetime(user_input)
trade_table1 = trade_table.copy()
eod_table1 = eod_table.copy()
trade_table1['Trade date'] = \
pd.to_datetime(trade_table['Trade date'])
eod_table1['Date'] = \
pd.to_datetime(eod_table['Date'])

first_of_month = pd.to_datetime(str(test_date.year)+\
	str(test_date.month)+'01' if test_date.month>=10
	else str(test_date.year)+ '0'+\
	str(test_date.month)+'01')
first_of_year = pd.to_datetime(str(test_date.year)+'0101')
trades_to_date = trade_table1[trade_table1['Trade date']<=user_input]
prices_to_date = trade_table1[trade_table1['Trade date']<=user_input]

trades_to_date_with_multipliers = \
trades_to_date.merge(contract_and_instrument)

trades_to_date_with_multipliers['contract_volume'] = \
trades_to_date_with_multipliers['Traded amount']\
*trades_to_date_with_multipliers['Contract Multiplier']\

today_positions = trades_to_date_with_multipliers.groupby(['Instrument Asset Class','Contract Ticker'])['contract_volume'].sum()

print('\n\n\n')
print('Positions \n',today_positions)

today_prices = eod_table1[eod_table1['Date'] == test_date].T
today_prices1 = today_prices.rename(\
	columns= {today_prices.columns[0]:'prices'})

today_positions1 = trades_to_date_with_multipliers.groupby(['Contract Ticker'])['contract_volume'].sum()

today_prices_and_positions = today_positions1.to_frame().join(today_prices1)


valuation = pd.DataFrame((today_prices_and_positions['contract_volume']\
* today_prices_and_positions['prices']),columns = ['valuation'])


valuation2 = valuation.reset_index().merge(contract_and_instrument)


valuations = valuation2.groupby('Instrument Asset Class')['valuation'].sum()

print('\n\n\n')
print('Valuations\n')
print(valuations)

mask_day = (trade_table1['Trade date']==test_date)

mask_month = (trade_table1['Trade date']<=test_date)&\
(trade_table1['Trade date']>=first_of_month)

mask_year = (trade_table1['Trade date']<=test_date)&\
(trade_table1['Trade date']>=first_of_year)

trades_daily = trade_table1[mask_day]
trades_mtd = trade_table1[mask_month]
trades_ytd = trade_table1[mask_year]

def get_pnl(trades):
	trades_with_multipliers = trades.merge(contract_and_instrument)
	trades_with_multipliers['total_usd_trade'] = \
	trades_with_multipliers['Traded amount']*\
	trades_with_multipliers['Avg Price traded']*\
	trades_with_multipliers['Contract Multiplier']
	unrealised =  trades_with_multipliers\
	.groupby(['Instrument Asset Class','Contract Ticker'])\
	['total_usd_trade'].sum()
	trades_with_multipliers['contract_volume'] =\
	trades_with_multipliers['Traded amount']*\
	trades_with_multipliers['Contract Multiplier']
	positions = trades_with_multipliers.groupby('Contract Ticker')['contract_volume'].sum()
	prices_and_positions = positions.to_frame()\
	.join(today_prices1)\
	.join(contract_and_instrument\
	.set_index('Contract Ticker'))\
	.reset_index()
	prices_and_positions['current_value']= \
	prices_and_positions['contract_volume']\
	*prices_and_positions['prices']
	realised = -1*prices_and_positions\
	.groupby(['Instrument Asset Class', 'Contract Ticker'])['current_value'].sum()
	total_pnl = realised + unrealised
	return total_pnl

pnl_daily = get_pnl(trades_daily)

pnl_mtd = get_pnl(trades_mtd)

pnl_ytd = get_pnl(trades_ytd)

pnl_dict = {'daily': pnl_daily, 'mtd': pnl_mtd,'ytd': pnl_ytd}
print('\n\n\n')
for k,v in pnl_dict.items():
	print(k+' PnL', ' \n', v,'\n\n\n')
