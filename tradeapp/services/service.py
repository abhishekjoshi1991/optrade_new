from datetime import datetime
from requests import Session
from flask import request
import time
# from ..util import live_cache
from sqlalchemy import Date, cast
import pandas as pd
import numpy as np
from pandas import json_normalize
import csv
import json
import matplotlib.pyplot as plt
from tradeapp.models.models import OptionChain, db
from config import FUTURE_PRICE
from sqlalchemy import desc, func
import random

class NSELive:
    time_out = 5
    base_url = "https://www.nseindia.com"
    page_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    _routes = {
            "option_chain_indices": "/api/option-chain-indices",
            # "derivatives":"/get-quotes/equity",
            # "derivatives":"/api/historical/fo/derivatives",
            "derivatives":"/api/quote-derivative"
            
    }
    
    def __init__(self):
        self.s = Session()
        h = {
            "Host": "www.nseindia.com",
            "Referer": "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",
            "X-Requested-With": "XMLHttpRequest",
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-type": "application/json"
            }
        self.s.headers.update(h)
        self.s.get(self.page_url)
    
    def replaceNaN(self,df):
        if df.dtypes  == "float64" or df.dtypes  == "int64" :
            df = df.fillna(0, inplace=True)
            return df
        else:
            df = df.fillna('', inplace=True)
            return df
            
    def get(self, route, payload={}):
        # import pdb; pdb.set_trace()
        start_time = time.time()
        url = self.base_url + self._routes[route]
        # print("url--------get------------",url)
        response = self.s.get(url, params=payload) 
        # print("------------------", response.status_code)
        # print("------------------", response.text)     
        dict = response.json()
        df = json_normalize(dict["records"]["data"])
        # new line
        df['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:00")
        df.apply(self.replaceNaN)
        # print(df)
        objects = []
        # df.drop(['_sa_instance_state'], axis=1, inplace=True)

        for index, row in df.iterrows():
            # save = OptionChainCRUD(row)
            objects.append(OptionChain(strike_price=row["strikePrice"],
                        expiry_date=row["expiryDate"],
                        ce_strike_price=row["CE.strikePrice"],
                        ce_expiry_date= row["CE.expiryDate"],
                        ce_underlying=row["CE.underlying"],
                        ce_identifier=row["CE.identifier"],
                        ce_open_interest=row["CE.openInterest"],
                        ce_changein_open_interest=row["CE.changeinOpenInterest"],
                        ce_pchangein_open_interest= row["CE.pchangeinOpenInterest"],
                        ce_total_traded_volume=row["CE.totalTradedVolume"],
                        ce_implied_volatility=row["CE.impliedVolatility"],
                        ce_last_price=row["CE.lastPrice"],
                        ce_change=row["CE.change"],
                        ce_pchange=row["CE.pChange"],
                        ce_total_buy_quantity=row["CE.totalBuyQuantity"],
                        ce_total_sell_quantity=row["CE.totalSellQuantity"],
                        ce_bid_qty=row["CE.bidQty"],
                        ce_bidprice=row["CE.bidprice"],
                        ce_ask_qty= row["CE.askQty"],
                        ce_ask_price=row["CE.askPrice"],
                        ce_underlying_value=row["CE.underlyingValue"],
                        pe_strike_price=row["PE.strikePrice"],
                        pe_expiry_date= row["PE.expiryDate"],
                        pe_underlying=row["PE.underlying"],
                        pe_identifier=row["PE.identifier"],
                        pe_open_interest=row["PE.openInterest"],
                        pe_changein_open_interest=row["PE.changeinOpenInterest"],
                        pe_pchangein_open_interest=row["PE.changeinOpenInterest"],
                        pe_total_traded_volume=row["PE.totalTradedVolume"],
                        pe_implied_volatility= row["PE.impliedVolatility"],
                        pe_last_price= row["PE.lastPrice"],
                        pe_change=row["PE.change"],
                        pe_pchange=row["PE.pChange"],
                        pe_total_buy_quantity=row["PE.totalBuyQuantity"],
                        pe_total_sell_quantity=row["PE.totalSellQuantity"],
                        pe_bid_qty=row["PE.bidQty"],
                        pe_bidprice=row["PE.bidprice"],
                        pe_ask_qty=row["PE.askQty"],
                        pe_ask_price=row["PE.askPrice"],
                        pe_underlying_value=row["PE.underlyingValue"],
                        created_at=row["created_at"]
                        ))
            # objects.append(OptionChainCRUD(row))
            # save.post()
        db.session.bulk_save_objects(objects)
        db.session.commit()
        print('------------>>', time.time() - start_time)
        resp = {}
        resp["code"] = 200
        resp["message"] = "Data saved successfully!!!" 
        return resp

    def option_chain_indices(self, symbol):
        data = {"symbol": symbol}
        return self.get("option_chain_indices", data) 
    
    def derivatives(self, symbol):
        data = {"symbol": symbol}
        url = self.base_url + self._routes['derivatives']
        response = self.s.get(url, params=data) 
        print("------------------", response.url)
        dict = response.json()
        df = pd.DataFrame()
        for i in dict["stocks"]:
            if df.empty:
                df = json_normalize(i["metadata"])
            else:
                df.loc[len(df.index)] = i["metadata"]
           
        df.apply(self.replaceNaN)
        # print(df['identifier'])
        
        for index, row in df.iterrows():
            print(row)
            if row["optionType"] == "Put" :
                items = OptionChain.query.filter_by(pe_identifier =row["identifier"])
                for i in items:
                    print("---------------------->pe")
                    i.pe_open = row["openPrice"]
                    i.pe_close = row["closePrice"]
                    i.pe_high = row["highPrice"]
                    i.pe_low = row["lowPrice"]
                    db.session.commit()
            else:
                items = OptionChain.query.filter_by(ce_identifier =row["identifier"])
            # print(items)
                for i in items:
                    print("---------------------->ce")
                    i.ce_open = row["openPrice"]
                    i.ce_close = row["closePrice"]
                    i.ce_high = row["highPrice"]
                    i.ce_low = row["lowPrice"]
                    db.session.commit()
            # break
               
        
        # UPDATE option_chain, 
        # SET open = openPrice, close = closePrice, high=highPrice, low = lowPrice,
        # WHERE option_chain.ce_identifier = identifier or 
        # df.to_csv("derivatives.csv")

        resp = {}
        resp["code"] = 200
        resp["message"] = "Data saved successfully!!!" 
        return resp

    # New function
    def co_po_chart(self):
        # import pdb; pdb.set_trace()
        # latest_date = OptionChain.query.order_by(OptionChain.id.desc()).first().created_at
        latest_date = db.session.query(OptionChain.created_at).group_by(OptionChain.created_at).all()[-2][0]

        print(latest_date)
        latest_date_records = OptionChain.query.filter(OptionChain.created_at==latest_date).all()
        pd.set_option('display.max_columns', False)
        df = pd.DataFrame([vars(s) for s in latest_date_records])[['strike_price', 'expiry_date', 'ce_open_interest', 'pe_open_interest', 'created_at']]
        if request.method == 'GET':
            expiry_dates = list(set(df['expiry_date'].to_list()))
            expiry_dates.sort(key=lambda date: datetime.strptime(date, "%d-%b-%Y"))
            return expiry_dates
        if request.method == 'POST':
            form_data = json.loads(request.data)
            e_date = form_data['expiry']
            filt_data = df['expiry_date'] == e_date
            filtered_df = df[filt_data]
            filtered_df[['strike_price', 'ce_open_interest', 'pe_open_interest']] = filtered_df[
                ['strike_price', 'ce_open_interest', 'pe_open_interest']].astype(int)
            strike_price_list = filtered_df['strike_price'].to_list()
            vals = {
                'strike_price': strike_price_list,
                'dataset': [
                {
                    'label': 'CE OI',
                    'data': filtered_df['ce_open_interest'].to_list(),
                    'backgroundColor': 'rgb(240, 38, 38)'
                },
                {
                    'label': 'PE OI',
                    'data': filtered_df['pe_open_interest'].to_list(),
                    'backgroundColor': 'rgb(9, 237, 120)'
                }]}
            print(strike_price_list)
            print(vals)
            return vals

    def co_po_change_chart(self):
        # latest_date = OptionChain.query.order_by(OptionChain.id.desc()).first().created_at
        latest_date = db.session.query(OptionChain.created_at).group_by(OptionChain.created_at).all()[-2][0]
        print(latest_date)
        latest_date_records = OptionChain.query.filter(OptionChain.created_at == latest_date).all()
        pd.set_option('display.max_columns', False)
        df = pd.DataFrame([vars(s) for s in latest_date_records])[
            ['strike_price', 'expiry_date', 'ce_changein_open_interest', 'pe_changein_open_interest', 'created_at']]
        if request.method == 'GET':
            expiry_dates = list(set(df['expiry_date'].to_list()))
            expiry_dates.sort(key=lambda date: datetime.strptime(date, "%d-%b-%Y"))
            return expiry_dates
        if request.method == 'POST':
            form_data = json.loads(request.data)
            e_date = form_data['expiry']
            filt_data = df['expiry_date'] == e_date
            filtered_df = df[filt_data]
            filtered_df[['strike_price', 'ce_changein_open_interest', 'pe_changein_open_interest']] = filtered_df[
                ['strike_price', 'ce_changein_open_interest', 'pe_changein_open_interest']].astype(int)
            strike_price_list = filtered_df['strike_price'].to_list()
            vals = {
                'strike_price': strike_price_list,
                'dataset': [
                    {
                        'label': 'CE OI Change',
                        'data': filtered_df['ce_changein_open_interest'].to_list(),
                        'backgroundColor': 'rgb(240, 38, 38)'
                    },
                    {
                        'label': 'PE OI Change',
                        'data': filtered_df['pe_changein_open_interest'].to_list(),
                        'backgroundColor': 'rgb(9, 237, 120)'
                    }]}
            print(strike_price_list)
            print(vals)
            return vals

    # to plot multistrike line chart for OI/OI CHG
    def multi_strike_line_chart(self):
        print('%%%%%%%%%%% multistrike api called')

        latest_date = db.session.query(OptionChain.created_at).group_by(OptionChain.created_at).all()[-2][0]
        print(latest_date)
        latest_date_records = OptionChain.query.filter(OptionChain.created_at == latest_date).all()
        df = pd.DataFrame([vars(s) for s in latest_date_records])
        if request.method == 'GET':
            df['strike_price'] = df['strike_price'].astype(int)
            strike_prices = list(set(df['strike_price'].to_list()))
            strike_prices.sort()
            expiry_dates = list(set(df['expiry_date'].to_list()))
            expiry_dates.sort(key=lambda date: datetime.strptime(date, "%d-%b-%Y"))
            expiry_date_list = []
            # count = 1
            for exp in expiry_dates:
                expiry_date_list.append({'label': exp, 'value': exp})
                # count += 1
            print('==========', expiry_date_list)

            return expiry_date_list
        if request.method == 'POST':
            # import pdb;
            # pdb.set_trace()
            # today_date = datetime.today().strftime('%Y-%m-%d')
            today_date = '2023-03-09'
            today_date_records = db.session.query(OptionChain).filter(cast(OptionChain.created_at, Date) == today_date).all()
            today_df = pd.DataFrame([vars(s) for s in today_date_records])
            if today_date_records:
                today_df['created_at'] = pd.to_datetime(today_df['created_at'])
                today_df['time'] = pd.to_datetime(today_df['created_at']).dt.strftime('%H:%M')
                req = json.loads(request.data)
                expiry = req.get('expiry')
                strikes = req.get('strikes')
                OI = req.get('OI')
                OICHG = req.get('OICHG')
                final_vals = []
                for exp in expiry:
                    for strike in strikes:
                        filt_df = today_df[(today_df['strike_price'] == int(strike.split(' ')[0])) & (today_df['expiry_date'] == exp)]
                        color_1 = random.randint(0, 255)
                        color_2 = random.randint(0, 255)
                        color_3 = random.randint(0, 255)
                        if OI:
                            if strike.split(' ')[-1] == 'CE':
                                ce_oi_data = dict(zip(filt_df.time, filt_df.ce_open_interest))
                                final_vals.append({
                                    'label': strike + ' OI ' + str(exp),
                                    'data': ce_oi_data,
                                    'borderColor': 'rgb({}, {}, {})'.format(color_1, color_2, color_3),
                                })
                            else:
                                pe_oi_data = dict(zip(filt_df.time, filt_df.pe_open_interest))
                                final_vals.append({
                                    'label': strike + ' OI ' + str(exp),
                                    'data': pe_oi_data,
                                    'borderColor': 'rgb({}, {}, {})'.format(color_1, color_2, color_3),
                                })
                        if OICHG:
                            if strike.split(' ')[-1] == 'CE':
                                ce_oi_change_data = dict(zip(filt_df.time, filt_df.ce_changein_open_interest))
                                final_vals.append({
                                    'label': strike + ' OICHG ' + str(exp),
                                    'data': ce_oi_change_data,
                                    'borderColor': 'rgb({}, {}, {})'.format(color_1, color_2, color_3),
                                })
                            else:
                                pe_oi_change_data = dict(zip(filt_df.time, filt_df.pe_changein_open_interest))
                                final_vals.append({
                                    'label': strike + ' OICHG ' + str(exp),
                                    'data': pe_oi_change_data,
                                    'borderColor': 'rgb({}, {}, {})'.format(color_1, color_2, color_3),
                                })
                print('**********', final_vals)
                return final_vals
            else:
                return 'Data is not present for today'

    # to plot cumulative OI/OI Change line chart
    def cumulative_change_chart(self):
        print('%%%%%%%%%%% cunulative api called')
        latest_date = db.session.query(OptionChain.created_at).group_by(OptionChain.created_at).all()[-2][0]
        latest_date_records = OptionChain.query.filter(OptionChain.created_at == latest_date).all()
        df = pd.DataFrame([vars(s) for s in latest_date_records])
        if request.method == 'GET':
            df['strike_price'] = df['strike_price'].astype(int)
            strike_prices = list(set(df['strike_price'].to_list()))
            strike_prices.sort()
            expiry_dates = list(set(df['expiry_date'].to_list()))
            expiry_dates.sort(key=lambda date: datetime.strptime(date, "%d-%b-%Y"))
            return expiry_dates
        if request.method == 'POST':
            # import pdb;
            # pdb.set_trace()
            # today_date = datetime.today().strftime('%Y-%m-%d')
            today_date = '2023-03-09'
            today_date_records = db.session.query(OptionChain).filter(
                cast(OptionChain.created_at, Date) == today_date).all()
            today_df = pd.DataFrame([vars(s) for s in today_date_records])
            print(today_df)
            # today_df.to_csv('sample4.csv')
            if today_date_records:
                today_df['created_at'] = pd.to_datetime(today_df['created_at'])
                today_df['time'] = pd.to_datetime(today_df['created_at']).dt.strftime('%H:%M')
                req = json.loads(request.data)
                print(req)
                expiry = req.get('expiry')
                strikes = req.get('strikes')
                cum_strike = req.get('cumstrike')
                cum_exp = req.get('cumexp')
                OI = req.get('OI')
                OICHG = req.get('OICHG')
                final_vals = []
                ce_strikes = []
                pe_strikes = []
                for strike in strikes:
                    if strike.split(' ')[-1] == 'CE':
                        ce_strikes.append(int(strike.split(' ')[0]))
                    else:
                        pe_strikes.append(int(strike.split(' ')[0]))

                if cum_strike and cum_exp:
                    print('both are called')
                    ce_filt_grp_df = today_df[(today_df['strike_price'].isin(ce_strikes)) & (today_df['expiry_date'].isin(expiry))][
                        ['time', 'ce_open_interest','ce_changein_open_interest']].groupby(['time']).sum().reset_index()
                    pe_filt_grp_df = today_df[(today_df['strike_price'].isin(pe_strikes)) & (today_df['expiry_date'].isin(expiry))][
                        ['time', 'pe_open_interest','pe_changein_open_interest']].groupby(['time']).sum().reset_index()
                    ce_filt_grp_df['ce_open_interest'] = ce_filt_grp_df['ce_open_interest'].astype(int)
                    ce_filt_grp_df['ce_changein_open_interest'] = ce_filt_grp_df['ce_changein_open_interest'].astype(
                        int)
                    pe_filt_grp_df['pe_open_interest'] = pe_filt_grp_df['pe_open_interest'].astype(int)
                    pe_filt_grp_df['pe_changein_open_interest'] = pe_filt_grp_df['pe_changein_open_interest'].astype(
                        int)
                    if OI:
                        cumulative_ce_oi = dict(
                            zip(ce_filt_grp_df.time, ce_filt_grp_df.ce_open_interest))
                        cumulative_pe_oi = dict(
                            zip(pe_filt_grp_df.time, pe_filt_grp_df.pe_open_interest))
                        # diff_oi = {key: cumulative_pe_oi[key] - cumulative_ce_oi.get(key, 0) for key in
                        #            cumulative_ce_oi}

                        final_vals.append({'label': 'Calls ', 'data': cumulative_ce_oi})
                        final_vals.append({'label': 'Puts ', 'data': cumulative_pe_oi})
                        # final_vals.append({'label': 'Diff ' + exp, 'data': diff_oi})

                    if OICHG:
                        cumulative_ce_oi_change = dict(
                            zip(ce_filt_grp_df.time, ce_filt_grp_df.ce_changein_open_interest))
                        cumulative_pe_oi_change = dict(
                            zip(pe_filt_grp_df.time, pe_filt_grp_df.pe_changein_open_interest))
                        # diff_oi_change = {key: cumulative_pe_oi_change[key] - cumulative_ce_oi_change.get(key, 0) for
                        #                   key in cumulative_ce_oi_change}

                        final_vals.append({'label': 'Calls ', 'data': cumulative_ce_oi_change})
                        final_vals.append({'label': 'Puts ', 'data': cumulative_pe_oi_change})
                        # final_vals.append({'label': 'Diff ' + exp, 'data': diff_oi_change})

                    print(final_vals)
                    return final_vals

                # condition 1, strikes are combined and not expiries
                if cum_strike:
                    print('&&&&&&&&&&&& cum strike true')
                    ce_filt_grp_df = today_df[(today_df['strike_price'].isin(ce_strikes)) & (today_df['expiry_date'].isin(expiry))][['time','expiry_date','ce_open_interest','ce_changein_open_interest']].groupby(['time','expiry_date']).sum().reset_index()
                    pe_filt_grp_df = today_df[(today_df['strike_price'].isin(pe_strikes)) & (today_df['expiry_date'].isin(expiry))][['time','expiry_date','pe_open_interest','pe_changein_open_interest']].groupby(['time','expiry_date']).sum().reset_index()
                    ce_filt_grp_df['ce_open_interest'] = ce_filt_grp_df['ce_open_interest'].astype(int)
                    ce_filt_grp_df['ce_changein_open_interest'] = ce_filt_grp_df['ce_changein_open_interest'].astype(int)
                    pe_filt_grp_df['pe_open_interest'] = pe_filt_grp_df['pe_open_interest'].astype(int)
                    pe_filt_grp_df['pe_changein_open_interest'] = pe_filt_grp_df['pe_changein_open_interest'].astype(int)
                    for exp in expiry:
                        filt_based_expiry_ce_df = ce_filt_grp_df[ce_filt_grp_df['expiry_date'] == exp]
                        filt_based_expiry_pe_df = pe_filt_grp_df[pe_filt_grp_df['expiry_date'] == exp]
                        if OI:
                            cumulative_ce_oi = dict(zip(filt_based_expiry_ce_df.time, filt_based_expiry_ce_df.ce_open_interest))
                            cumulative_pe_oi = dict(zip(filt_based_expiry_pe_df.time, filt_based_expiry_pe_df.pe_open_interest))
                            diff_oi = {key: cumulative_pe_oi[key] - cumulative_ce_oi.get(key, 0) for key in cumulative_ce_oi}

                            final_vals.append({'label': 'Calls '+exp, 'data': cumulative_ce_oi})
                            final_vals.append({'label': 'Puts '+exp, 'data': cumulative_pe_oi})
                            final_vals.append({'label': 'Diff '+exp, 'data': diff_oi})

                        if OICHG:
                            cumulative_ce_oi_change = dict(zip(filt_based_expiry_ce_df.time, filt_based_expiry_ce_df.ce_changein_open_interest))
                            cumulative_pe_oi_change = dict(zip(filt_based_expiry_pe_df.time, filt_based_expiry_pe_df.pe_changein_open_interest))
                            diff_oi_change = {key: cumulative_pe_oi_change[key] - cumulative_ce_oi_change.get(key, 0) for key in cumulative_ce_oi_change}

                            final_vals.append({'label': 'Calls '+exp, 'data': cumulative_ce_oi_change})
                            final_vals.append({'label': 'Puts '+exp, 'data': cumulative_pe_oi_change})
                            final_vals.append({'label': 'Diff '+exp, 'data': diff_oi_change})

                    print(final_vals)
                    return final_vals

                if cum_exp:
                    print('***********cum exp true')
                    ce_filt_grp_df = \
                    today_df[(today_df['strike_price'].isin(ce_strikes)) & (today_df['expiry_date'].isin(expiry))][
                        ['time', 'ce_open_interest', 'ce_changein_open_interest','strike_price']].groupby(
                        ['time', 'strike_price']).sum().reset_index()
                    pe_filt_grp_df = \
                    today_df[(today_df['strike_price'].isin(pe_strikes)) & (today_df['expiry_date'].isin(expiry))][
                        ['time', 'pe_open_interest', 'pe_changein_open_interest','strike_price']].groupby(
                        ['time', 'strike_price']).sum().reset_index()
                    ce_filt_grp_df['ce_open_interest'] = ce_filt_grp_df['ce_open_interest'].astype(int)
                    ce_filt_grp_df['ce_changein_open_interest'] = ce_filt_grp_df['ce_changein_open_interest'].astype(
                        int)
                    pe_filt_grp_df['pe_open_interest'] = pe_filt_grp_df['pe_open_interest'].astype(int)
                    pe_filt_grp_df['pe_changein_open_interest'] = pe_filt_grp_df['pe_changein_open_interest'].astype(
                        int)
                    ce_filt_grp_df['strike_price'] = ce_filt_grp_df['strike_price'].astype(int)
                    pe_filt_grp_df['strike_price'] = pe_filt_grp_df['strike_price'].astype(int)
                    for ce_strk in ce_strikes:
                        filt_based_strike_ce_df = ce_filt_grp_df[ce_filt_grp_df['strike_price'] == ce_strk]
                        if OI:
                            cumulative_ce_oi = dict(zip(filt_based_strike_ce_df.time, filt_based_strike_ce_df.ce_open_interest))
                            final_vals.append({'label': 'Calls '+str(ce_strk), 'data': cumulative_ce_oi})
                        if OICHG:
                            cumulative_ce_oi_change = dict(zip(filt_based_strike_ce_df.time, filt_based_strike_ce_df.ce_changein_open_interest))
                            final_vals.append({'label': 'Calls '+str(ce_strk), 'data': cumulative_ce_oi_change})

                    for pe_strk in pe_strikes:
                        filt_based_strike_pe_df = pe_filt_grp_df[pe_filt_grp_df['strike_price'] == pe_strk]
                        if OI:
                            cumulative_pe_oi = dict(zip(filt_based_strike_pe_df.time, filt_based_strike_pe_df.pe_open_interest))
                            # diff_oi = {key: cumulative_pe_oi[key] - cumulative_ce_oi.get(key, 0) for key in cumulative_ce_oi}

                            final_vals.append({'label': 'Puts '+str(pe_strk), 'data': cumulative_pe_oi})
                            # final_vals.append({'label': 'Diff '+str(strk), 'data': diff_oi})
                        if OICHG:
                            cumulative_pe_oi_change = dict(zip(filt_based_strike_pe_df.time, filt_based_strike_pe_df.pe_changein_open_interest))
                            # diff_oi_change = {key: cumulative_pe_oi_change[key] - cumulative_ce_oi_change.get(key, 0) for key in cumulative_ce_oi_change}

                            final_vals.append({'label': 'Puts '+str(pe_strk), 'data': cumulative_pe_oi_change})
                            # final_vals.append({'label': 'Diff '+str(strk), 'data': diff_oi_change})
                    print(final_vals)
                    return final_vals

    # Function will return strike prices based on expiry date selected
    def get_price_for_multi_strike(self):
        # import pdb; pdb.set_trace()
        print('=====$$$$$$=========', request.data)
        expiry = json.loads(request.data)[0]
        latest_date = db.session.query(OptionChain.created_at).group_by(OptionChain.created_at).all()[-2][0]
        print(latest_date)
        latest_date_records = OptionChain.query.filter(OptionChain.created_at == latest_date).all()
        df = pd.DataFrame([vars(s) for s in latest_date_records])
        filt_data = df['expiry_date'] == expiry
        filtered_df = df[filt_data]
        filtered_df['strike_price'] = filtered_df['strike_price'].astype(int)
        strike_prices = list(set(filtered_df['strike_price'].to_list()))
        strike_prices.sort()
        print('$$$$$$$', strike_prices)
        options = ['CE', 'PE']
        strike_price_list = []
        count = 1
        for price in strike_prices:
            for opt in options:
                strike_price_list.append({'Strike': str(price) + ' ' + opt, 'id': count})
                count += 1
        print('===============', strike_price_list)
        return strike_price_list

    def max_pain_chart(self):
        # import pdb; pdb.set_trace()
        latest_date = db.session.query(OptionChain.created_at).group_by(OptionChain.created_at).all()[-2][0]
        print(latest_date)
        latest_date_records = OptionChain.query.filter(OptionChain.created_at == latest_date).all()
        df = pd.DataFrame([vars(s) for s in latest_date_records])[
            ['strike_price', 'expiry_date', 'ce_open_interest', 'pe_open_interest', 'created_at']]
        if request.method == 'GET':
            expiry_dates = list(set(df['expiry_date'].to_list()))
            expiry_dates.sort(key=lambda date: datetime.strptime(date, "%d-%b-%Y"))
            return expiry_dates
        if request.method == 'POST':
            # import pdb;
            # pdb.set_trace()
            req = json.loads(request.data)
            expiry = req.get('expiry')
            filt_data = df['expiry_date'] == expiry
            df = df[filt_data]

            # ac_col = [273250,
            #           9700,
            #           70750,
            #           4250,
            #           16150,
            #           7200,
            #           1348750,
            #           4150,
            #           9800,
            #           2350,
            #           125250,
            #           2100,
            #           193700,
            #           8700,
            #           29400,
            #           2600,
            #           1426050,
            #           4600,
            #           41850,
            #           6750,
            #           418600,
            #           6700,
            #           666050,
            #           11000,
            #           373350,
            #           63400,
            #           3823950,
            #           64750,
            #           1881650,
            #           162200,
            #           4041600,
            #           371100,
            #           3346550,
            #           573200,
            #           2321450,
            #           887650,
            #           4857200,
            #           1781250,
            #           3550450,
            #           1526250,
            #           4609950,
            #           1814500,
            #           4683150,
            #           1787250,
            #           6336650,
            #           1382350,
            #           5518650,
            #           233850,
            #           1250300,
            #           190150,
            #           1244100,
            #           102850,
            #           691750,
            #           60000,
            #           835550,
            #           21700,
            #           854400,
            #           16500,
            #           114200,
            #           9500,
            #           66550,
            #           8350,
            #           121700,
            #           6100,
            #           60500,
            #           3650,
            #           262200,
            #           5300,
            #           53600,
            #           3800,
            #           11950,
            #           250,
            #           10000,
            #           250,
            #           7150,
            #           100,
            #           491800,
            #           2100,
            #           9100,
            #           100,
            #           77800,
            #           0,
            #           750,
            #           0,
            #           12550,
            #           ]
            #
            # ad_col = [44600,
            #           0,
            #           1050,
            #           0,
            #           0,
            #           0,
            #           459100,
            #           50,
            #           2350,
            #           50,
            #           2500,
            #           100,
            #           1550,
            #           0,
            #           2400,
            #           0,
            #           192400,
            #           3550,
            #           6600,
            #           150,
            #           5750,
            #           700,
            #           22300,
            #           2250,
            #           12600,
            #           3350,
            #           382950,
            #           2250,
            #           21000,
            #           2450,
            #           136900,
            #           5100,
            #           142350,
            #           11000,
            #           98550,
            #           6200,
            #           682500,
            #           15700,
            #           213200,
            #           24250,
            #           407250,
            #           99200,
            #           869850,
            #           246150,
            #           3148850,
            #           959350,
            #           5652750,
            #           792350,
            #           2872450,
            #           1135350,
            #           4315850,
            #           1101100,
            #           3324550,
            #           1003550,
            #           3155050,
            #           767500,
            #           5207000,
            #           310650,
            #           2204200,
            #           518800,
            #           1762400,
            #           613300,
            #           1997700,
            #           172800,
            #           1402550,
            #           162300,
            #           3692350,
            #           110250,
            #           757750,
            #           112850,
            #           1143550,
            #           58950,
            #           1103650,
            #           33950,
            #           934500,
            #           28100,
            #           3372300,
            #           257900,
            #           351950,
            #           21250,
            #           827150,
            #           27500,
            #           455000,
            #           19350,
            #           1319300,
            #           ]
            #
            # z_col = [20300,
            #          20250,
            #          20200,
            #          20150,
            #          20100,
            #          20050,
            #          20000,
            #          19950,
            #          19900,
            #          19850,
            #          19800,
            #          19750,
            #          19700,
            #          19650,
            #          19600,
            #          19550,
            #          19500,
            #          19450,
            #          19400,
            #          19350,
            #          19300,
            #          19250,
            #          19200,
            #          19150,
            #          19100,
            #          19050,
            #          19000,
            #          18950,
            #          18900,
            #          18850,
            #          18800,
            #          18750,
            #          18700,
            #          18650,
            #          18600,
            #          18550,
            #          18500,
            #          18450,
            #          18400,
            #          18350,
            #          18300,
            #          18250,
            #          18200,
            #          18150,
            #          18100,
            #          18050,
            #          18000,
            #          17950,
            #          17900,
            #          17850,
            #          17800,
            #          17750,
            #          17700,
            #          17650,
            #          17600,
            #          17550,
            #          17500,
            #          17450,
            #          17400,
            #          17350,
            #          17300,
            #          17250,
            #          17200,
            #          17150,
            #          17100,
            #          17050,
            #          17000,
            #          16950,
            #          16900,
            #          16850,
            #          16800,
            #          16750,
            #          16700,
            #          16650,
            #          16600,
            #          16550,
            #          16500,
            #          16450,
            #          16400,
            #          16350,
            #          16300,
            #          16250,
            #          16200,
            #          16150,
            #          16100,
            #          ]
            # data = {
            #     'strike_price': z_col,
            #     'pe_open_interest': ad_col,
            #     'ce_open_interest': ac_col}
            # df = pd.DataFrame(data)
            df = df.iloc[::-1]
            df['pe_pain'] = df[['strike_price', 'pe_open_interest']].prod(1).cumsum() - (df['strike_price'] * df['pe_open_interest'].cumsum())
            df['mult'] = df['strike_price'] * df['ce_open_interest']
            df['ce_pain'] = (df['ce_open_interest'].iloc[::-1].cumsum()[::-1] * df['strike_price']) - df['mult'].iloc[::-1].cumsum()[::-1]
            df['total_pain'] = df['ce_pain'] + df['pe_pain']
            print(df)
            reverse_df = df.iloc[::-1]
            dataset = {
                'labels': reverse_df['strike_price'].to_list(),
                'dataset': [
                        {
                            'label': "Total Pain",
                            'type': 'line',
                            'data': reverse_df['total_pain'].to_list(),
                            'backgroundColor': "#8c8c89",
                            'borderColor': "#8c8c89",
                            'pointRadius': 0
                        },
                        {
                          'label': "CE Pain",
                          'data': reverse_df['ce_pain'].to_list(),
                          'backgroundColor': "red",
                        },
                        {
                          'label': 'PE Pain',
                          'data': reverse_df['pe_pain'].to_list(),
                          'backgroundColor':'green'
                        }]
            }
            print(dataset)

            return dataset

    def max_pain_intraday_chart(self):
        pass
    
    def get_all(self):
        data = OptionChain.query.all()
        return data
    
    def ce_pe_formulea(self):
        data = OptionChain.query.all()
        df = pd.DataFrame([vars(s) for s in data])
        df.drop(['_sa_instance_state'], axis=1, inplace=True)
        # df.to_csv("df.csv")
        min_absolute_price = df['absolute_price'].min()
        sum_of_ce_open_interests = df['ce_open_interest'].sum()
        print(min_absolute_price)
     
        df["ce_intrinsic_value"] = df['ce_strike_price'].apply(lambda x :FUTURE_PRICE - x if  (x < FUTURE_PRICE) else 0)        
        df['ce_time_value'] = np.where((df['ce_last_price'] - df['ce_intrinsic_value'] )>= 0, df['ce_last_price'] - df['ce_intrinsic_value'], 0)
        df["pe_intrinsic_value"] = df['pe_strike_price'].apply(lambda x :FUTURE_PRICE - x if  (x > FUTURE_PRICE) else 0)
        
        df["pe_time_value"] = np.where((df['pe_last_price'] - df['pe_intrinsic_value'] )>= 0, df['pe_last_price'] - df['pe_intrinsic_value'], 0)
        
        df["ce_moneyness"] = df.apply(lambda row: self.ce_moneyness(row['absolute_price'], row['ce_strike_price'], min_absolute_price), axis=1)
        df["pe_moneyness"] = df.apply(lambda row: self.pe_moneyness(row['absolute_price'], row['pe_strike_price'], min_absolute_price), axis=1)
        # df["pe_moneyness"] = df["absolute_price"].apply(lambda x: "ATM" if (x == min_absolute_price) else None)
        
        df["pe_oi_minus_ce_oi"] = df['pe_open_interest'] - df['ce_open_interest']
        df["pe_oi_minus_ce_oi"] = df['pe_open_interest'] - df['ce_open_interest']
        df["pe_oi_change_minus_ce_oi_change"] =df['pe_changein_open_interest'] - df['ce_changein_open_interest']
        
        df["pcr_oi"] = np.where(df['ce_changein_open_interest'] != 0, df['pe_changein_open_interest'] / df['ce_changein_open_interest'], 0)
        df["pcr_volume"] = np.where(df['ce_total_traded_volume'] != 0, df['pe_total_traded_volume'] / df['ce_total_traded_volume'], 0)
        df["ce_pain"] = (df['ce_strike_price'] * sum_of_ce_open_interests) - sum(df["ce_open_interest"]*df["ce_strike_price"])
        df['pe_pain'] = df[['pe_open_interest', 'pe_strike_price']].prod(1).cumsum() - (df['pe_open_interest']*df['pe_strike_price'].cumsum())
        
        df["ce_oi_change_percentage"] = np.where((df["ce_open_interest"]-df["ce_changein_open_interest"]) != 0, df['ce_changein_open_interest'] /(df["ce_open_interest"]-df["ce_changein_open_interest"]), 0)
        df["pe_oi_change_percentage"] = np.where((df["pe_open_interest"]-df["pe_changein_open_interest"]) != 0, df['pe_changein_open_interest'] /(df["pe_open_interest"]-df["pe_changein_open_interest"]), 0)
        
        df["ce_oh"] = np.where(df["ce_open"] == df["ce_high"], "OH", "-")
        df["pe_oh"] = np.where(df["pe_open"] == df["pe_high"], "OH", "-")
        df["ce_ol"] = np.where(df["ce_open"] == df["ce_low"], "OL", "-")
        df["pe_ol"] = np.where(df["pe_open"] == df["ce_low"], "OL", "-")
        
        print(df[["ce_moneyness"]].head(50))
        
        return df.to_json(orient ='table')
        
    def ce_intrinsic_value(self, df):
        return FUTURE_PRICE - df['ce_strike_price'] if  df['ce_strike_price'] < FUTURE_PRICE else 0
    
    def ce_time_value(self, ce_last_price, ce_intrinsic_value):
        return ce_last_price - ce_intrinsic_value if (ce_last_price - ce_intrinsic_value) >= 0 else 0
    
    def pe_intrinsic_value(self, pe_strike_price):
        return FUTURE_PRICE - pe_strike_price if  pe_strike_price < FUTURE_PRICE else 0
    
    def pe_time_value(self, pe_last_price, pe_intrinsic_value):
        return pe_last_price - pe_intrinsic_value if (pe_last_price - pe_intrinsic_value) >= 0 else 0
    
    def ce_moneyness(self, absolute_price, ce_strike_price, min_absolute_price):
        if absolute_price == min_absolute_price:
            return "ATM" 
        elif ce_strike_price > FUTURE_PRICE:
            return "ITM"
        elif  ce_strike_price < FUTURE_PRICE:
            return "OTM"
        else:
            return None
    
    def pe_moneyness(self, absolute_price, pe_strike_price, min_absolute_price):
        if absolute_price == min_absolute_price:
            return "ATM" 
        elif pe_strike_price > FUTURE_PRICE:
            return "ITM"
        elif  pe_strike_price < FUTURE_PRICE:
            return "OTM"
        else:
            return None
    
    def pe_oi_minus_ce_oi(self, pe_open_interest,ce_open_interest):
        return pe_open_interest - ce_open_interest
    
    def pe_oi_change_minus_ce_oi_change(self, pe_changein_open_interest, ce_changein_open_interest):
        return pe_changein_open_interest - ce_changein_open_interest
    
    def pcr_oi(self, pe_changein_open_interest, ce_changein_open_interest):
        return pe_changein_open_interest/ce_changein_open_interest if ce_changein_open_interest != 0 else 0
    
    def pcr_volume(self, pe_total_traded_volume, ce_total_traded_volume):
        return pe_total_traded_volume / ce_total_traded_volume if ce_total_traded_volume != 0 else 0
    
    def ce_pain(self, ce_strike_price, sum_of_ce_open_interests):
        return ce_strike_price * sum_of_ce_open_interests
    
class OptionChainCRUD:
    def __init__(self, row):
        self._strike_price = row["strikePrice"]
        self._expiry_date = row["expiryDate"]
        self._ce_strike_price = row["CE.strikePrice"]
        self._ce_expiry_date = row["CE.expiryDate"]
        self._ce_underlying = row["CE.underlying"]
        self._ce_identifier = row["CE.identifier"]
        self._ce_open_interest = row["CE.openInterest"]
        self._ce_changein_open_interest = row["CE.changeinOpenInterest"]
        self._ce_pchangein_open_interest = row["CE.pchangeinOpenInterest"]
        self._ce_total_traded_volume = row["CE.totalTradedVolume"]
        self._ce_implied_volatility = row["CE.impliedVolatility"]
        self._ce_last_price = row["CE.lastPrice"]
        self._ce_change = row["CE.change"]
        self._ce_pchange = row["CE.pChange"]
        self._ce_total_buy_quantity = row["CE.totalBuyQuantity"]
        self._ce_total_sell_quantity = row["CE.totalSellQuantity"]
        self._ce_bid_qty = row["CE.bidQty"]
        self._ce_bidprice = row["CE.bidprice"]
        self._ce_ask_qty = row["CE.askQty"]
        self._ce_ask_price = row["CE.askPrice"]
        self._ce_underlying_value = row["CE.underlyingValue"]
        
        self._pe_strike_price = row["PE.strikePrice"]
        self._pe_expiry_date = row["PE.expiryDate"]
        self._pe_underlying = row["PE.underlying"]
        self._pe_identifier = row["PE.identifier"]
        self._pe_open_interest = row["PE.openInterest"]
        self._pe_changein_open_interest = row["PE.changeinOpenInterest"]
        self._pe_pchangein_open_interest = row["PE.pchangeinOpenInterest"]
        self._pe_total_traded_volume = row["PE.totalTradedVolume"]
        self._pe_implied_volatility = row["PE.impliedVolatility"]
        self._pe_last_price = row["PE.lastPrice"]
        self._pe_change = row["PE.change"]
        self._pe_pchange = row["PE.pChange"]
        self._pe_total_buy_quantity = row["PE.totalBuyQuantity"]
        self._pe_total_sell_quantity = row["PE.totalSellQuantity"]
        self._pe_bid_qty = row["PE.bidQty"]
        self._pe_bidprice = row["PE.bidprice"]
        self._pe_ask_qty = row["PE.askQty"]
        self._pe_ask_price = row["PE.askPrice"]
        self._pe_underlying_value = row["PE.underlyingValue"]
        self._created_at = row["created_at"]
        
        # GETTERS AND SETTERS
    
    def post(self):
        # print("inside post --------->>", self.get_strike_price)
        option_chain = OptionChain(       strike_price = self.strike_price,
                                expiry_date = self.expiry_date,
                                ce_strike_price = self.ce_strike_price, 
                                ce_expiry_date = self.ce_expiry_date,  
                                ce_underlying = self.ce_underlying,
                                ce_identifier = self.ce_identifier, 
                                ce_open_interest = self.ce_open_interest, 
                                ce_changein_open_interest = self.ce_changein_open_interest, 
                                ce_pchangein_open_interest = self.ce_pchangein_open_interest, 
                                ce_total_traded_volume = self.ce_total_traded_volume, 
                                ce_implied_volatility = self.ce_implied_volatility, 
                                ce_last_price = self.ce_last_price, 
                                ce_change = self.ce_change, 
                                ce_pchange = self.ce_pchange, 
                                ce_total_buy_quantity = self.ce_total_buy_quantity, 
                                ce_total_sell_quantity = self.ce_total_sell_quantity, 
                                ce_bid_qty = self.ce_bid_qty, 
                                ce_bidprice = self.ce_bidprice, 
                                ce_ask_qty = self.ce_ask_qty, 
                                ce_ask_price = self.ce_ask_price, 
                                ce_underlying_value = self.ce_underlying_value, 
                                pe_strike_price = self.pe_strike_price, 
                                pe_expiry_date = self.pe_expiry_date, 
                                pe_underlying = self.pe_underlying, 
                                pe_identifier = self.pe_identifier, 
                                pe_open_interest = self.pe_open_interest, 
                                pe_changein_open_interest = self.pe_changein_open_interest, 
                                pe_pchangein_open_interest = self.pe_pchangein_open_interest, 
                                pe_total_traded_volume = self.pe_total_traded_volume, 
                                pe_implied_volatility = self.pe_implied_volatility, 
                                pe_last_price = self.pe_last_price, 
                                pe_change = self.pe_change, 
                                pe_pchange = self.pe_pchange, 
                                pe_total_buy_quantity = self.pe_total_buy_quantity, 
                                pe_total_sell_quantity = self.pe_total_sell_quantity, 
                                pe_bid_qty = self.pe_bid_qty, 
                                pe_bidprice = self.pe_bidprice, 
                                pe_ask_qty = self.pe_ask_qty, 
                                pe_ask_price = self.pe_ask_price, 
                                pe_underlying_value = self.pe_underlying_value, 
                                created_at = self._created_at
                                        )

        db.session.add(option_chain)
        db.session.commit()

    
    
    # strike_price
    @property
    def strike_price(self):
        return self._strike_price
    
    @strike_price.setter
    def strike_price(self, value):
        self._strike_price = value
        
    # expiry_date
    @property
    def expiry_date(self):
        return self._expiry_date
    
    @expiry_date.setter
    def expiry_date(self, value):
        self._expiry_date = value
        
    # ce_strike_price
    @property
    def ce_strike_price(self):
        return self._ce_strike_price
    
    @ce_strike_price.setter
    def ce_strike_price(self, value):
        self._ce_strike_price = value
        
    # ce_expiry_date
    @property
    def ce_expiry_date(self):
        return self._ce_expiry_date
    
    @ce_expiry_date.setter
    def ce_expiry_date(self, value):
        self._ce_expiry_date = value
        
    # ce_underlying
    @property
    def ce_underlying(self):
        return self._ce_underlying
    
    @ce_underlying.setter
    def ce_underlying(self, value):
        self._ce_underlying = value
    
    # ce_identifier
    @property
    def ce_identifier(self):
        return self._ce_identifier
    
    @ce_identifier.setter
    def ce_identifier(self, value):
        self._ce_identifier = value
    
    # ce_open_interest
    @property
    def ce_open_interest(self):
        return self._ce_open_interest
    
    @ce_open_interest.setter
    def ce_open_interest(self, value):
        self._ce_open_interest = value
    
    # ce_changein_open_interest
    @property
    def ce_changein_open_interest(self):
        return self._ce_changein_open_interest
    
    @ce_changein_open_interest.setter
    def ce_changein_open_interest(self, value):
        self._ce_changein_open_interest = value
        
    # ce_pchangein_open_interest
    @property
    def ce_pchangein_open_interest(self):
        return self._ce_pchangein_open_interest
    
    @ce_pchangein_open_interest.setter
    def ce_pchangein_open_interest(self, value):
        self._ce_pchangein_open_interest = value
        
    # ce_total_traded_volume
    @property
    def ce_total_traded_volume(self):
        return self._ce_total_traded_volume
    
    @ce_total_traded_volume.setter
    def ce_total_traded_volume(self, value):
        self._ce_total_traded_volume = value
        
    # ce_implied_volatility
    @property
    def ce_implied_volatility(self):
        return self._ce_implied_volatility
    
    @ce_implied_volatility.setter
    def ce_implied_volatility(self, value):
        self._ce_implied_volatility = value
        
    # ce_last_price
    @property
    def ce_last_price(self):
        return self._ce_last_price
    
    @ce_last_price.setter
    def ce_last_price(self, value):
        self._ce_last_price = value
        
    # ce_change
    @property
    def ce_change(self):
        return self._ce_change
    
    @ce_change.setter
    def ce_change(self, value):
        self._ce_change = value
        
    # ce_pchange
    @property
    def ce_pchange(self):
        return self._ce_pchange
    
    @ce_change.setter
    def ce_pchange(self, value):
        self._ce_pchange = value
        
    # ce_total_buy_quantity
    @property
    def ce_total_buy_quantity(self):
        return self._ce_total_buy_quantity
    
    @ce_total_buy_quantity.setter
    def ce_total_buy_quantity(self, value):
        self._ce_total_buy_quantity = value
        
    # ce_total_sell_quantity
    @property
    def ce_total_sell_quantity(self):
        return self._ce_total_sell_quantity
    
    @ce_total_sell_quantity.setter
    def ce_total_sell_quantity(self, value):
        self._ce_total_sell_quantity = value
        
    # ce_bid_qty
    @property
    def ce_bid_qty(self):
        return self._ce_bid_qty
    
    @ce_bid_qty.setter
    def ce_bid_qty(self, value):
        self._ce_bid_qty = value
        
    # ce_bidprice
    @property
    def ce_bidprice(self):
        return self._ce_bidprice
    
    @ce_bidprice.setter
    def ce_bidprice(self, value):
        self._ce_bidprice = value
        
    # ce_ask_qty
    @property
    def ce_ask_qty(self):
        return self._ce_ask_qty
    
    @ce_ask_qty.setter
    def ce_ask_qty(self, value):
        self._ce_ask_qty = value
        
    # ce_ask_price
    @property
    def ce_ask_price(self):
        return self._ce_ask_price
    
    @ce_ask_price.setter
    def ce_ask_price(self, value):
        self._ce_ask_price = value
        
    # ce_underlying_value
    @property
    def ce_underlying_value(self):
        return self._ce_underlying_value
    
    @ce_underlying_value.setter
    def ce_underlying_value(self, value):
        self._ce_underlying_value = value
        
    # pe_strike_price
    @property
    def pe_strike_price(self):
        return self._pe_strike_price
    
    @pe_strike_price.setter
    def pe_strike_price(self, value):
        self._pe_strike_price = value
        
    # pe_expiry_date
    @property
    def pe_expiry_date(self):
        return self._pe_expiry_date
    
    @pe_expiry_date.setter
    def pe_expiry_date(self, value):
        self._pe_expiry_date = value
        
    # pe_underlying
    @property
    def pe_underlying(self):
        return self._pe_underlying
    
    @pe_underlying.setter
    def pe_underlying(self, value):
        self._pe_underlying = value
        
    # pe_identifier
    @property
    def pe_identifier(self):
        return self._pe_identifier
    
    @pe_identifier.setter
    def pe_identifier(self, value):
        self._pe_identifier = value
        
    # pe_open_interest
    @property
    def pe_open_interest(self):
        return self._pe_open_interest
    
    @pe_open_interest.setter
    def pe_open_interest(self, value):
        self._pe_open_interest = value

    # pe_changein_open_interest
    @property
    def pe_changein_open_interest(self):
        return self._pe_changein_open_interest
    
    @pe_changein_open_interest.setter
    def pe_changein_open_interest(self, value):
        self._pe_changein_open_interest = value

    # pe_pchangein_open_interest
    @property
    def pe_pchangein_open_interest(self):
        return self._pe_pchangein_open_interest
    
    @pe_pchangein_open_interest.setter
    def pe_pchangein_open_interest(self, value):
        self._pe_pchangein_open_interest = value

    # pe_total_traded_volume
    @property
    def pe_total_traded_volume(self):
        return self._pe_total_traded_volume
    
    @pe_total_traded_volume.setter
    def pe_total_traded_volume(self, value):
        self._pe_total_traded_volume = value

    # pe_implied_volatility
    @property
    def pe_implied_volatility(self):
        return self._pe_implied_volatility
    
    @pe_implied_volatility.setter
    def pe_implied_volatility(self, value):
        self._pe_implied_volatility = value

    # pe_last_price
    @property
    def pe_last_price(self):
        return self._pe_last_price
    
    @pe_last_price.setter
    def pe_last_price(self, value):
        self._pe_last_price = value

    # pe_change
    @property
    def pe_change(self):
        return self._pe_change
    
    @pe_change.setter
    def pe_change(self, value):
        self._pe_change = value

    # pe_pchange
    @property
    def pe_pchange(self):
        return self._pe_pchange
    
    @pe_pchange.setter
    def pe_pchange(self, value):
        self._pe_pchange = value

    # pe_total_buy_quantity
    @property
    def pe_total_buy_quantity(self):
        return self._pe_total_buy_quantity
    
    @pe_total_buy_quantity.setter
    def pe_total_buy_quantity(self, value):
        self._pe_total_buy_quantity = value

    # pe_total_sell_quantity
    @property
    def pe_total_sell_quantity(self):
        return self._pe_total_sell_quantity
    
    @pe_total_sell_quantity.setter
    def pe_total_sell_quantity(self, value):
        self._pe_total_sell_quantity = value

    # pe_bid_qty
    @property
    def pe_bid_qty(self):
        return self._pe_bid_qty
    
    @pe_bid_qty.setter
    def pe_bid_qty(self, value):
        self._pe_bid_qty = value

    # pe_bidprice
    @property
    def pe_bidprice(self):
        return self._pe_bidprice
    
    @pe_bidprice.setter
    def pe_bidprice(self, value):
        self._pe_bidprice = value

    # pe_ask_qty
    @property
    def pe_ask_qty(self):
        return self._pe_ask_qty
    
    @pe_ask_qty.setter
    def pe_ask_qty(self, value):
        self._pe_ask_qty = value

    # pe_ask_price
    @property
    def pe_ask_price(self):
        return self._pe_ask_price
    
    @pe_ask_price.setter
    def pe_ask_price(self, value):
        self._pe_ask_price = value

    # pe_underlying_value
    @property
    def pe_underlying_value(self):
        return self._pe_underlying_value
    
    @pe_underlying_value.setter
    def pe_underlying_value(self, value):
        self._pe_underlying_value = value

    # print("inside post --------->>", self.get_strike_price())
