from flask_sqlalchemy import SQLAlchemy
# from ...tradeapp import app
# import app

db = SQLAlchemy()


# Table for contries 
  
class OptionChain(db.Model):
    __tablename__ = 'option_chain'
    id = db.Column(db.Integer, primary_key=True)
    
    strike_price = db.Column(db.Float, nullable=True)
    expiry_date = db.Column(db.VARCHAR(200), nullable=True)
    ce_strike_price = db.Column(db.Float, nullable=True)
    ce_expiry_date = db.Column(db.VARCHAR(200), nullable=True)
    ce_underlying = db.Column(db.VARCHAR(200), nullable=True) 
    ce_identifier = db.Column(db.VARCHAR(200), nullable=True)
    ce_open_interest = db.Column(db.Float, nullable=True)
    ce_changein_open_interest = db.Column(db.Float, nullable=True)
    ce_pchangein_open_interest = db.Column(db.Float, nullable=True)
    ce_total_traded_volume = db.Column(db.Float, nullable=True)
    ce_implied_volatility = db.Column(db.Float, nullable=True)
    ce_last_price = db.Column(db.Float, nullable=True)
    ce_change = db.Column(db.Float, nullable=True)
    ce_pchange = db.Column(db.Float, nullable=True)
    ce_total_buy_quantity = db.Column(db.Float, nullable=True)
    ce_total_sell_quantity = db.Column(db.Float, nullable=True)
    ce_bid_qty = db.Column(db.Float, nullable=True)
    ce_bidprice = db.Column(db.Float, nullable=True)
    ce_ask_qty = db.Column(db.Float, nullable=True)
    ce_ask_price = db.Column(db.Float, nullable=True)
    ce_underlying_value =  db.Column(db.Float, nullable=True)
    # PUT CALL FIELDS
    pe_strike_price = db.Column(db.Float, nullable=True)
    pe_expiry_date = db.Column(db.VARCHAR(200), nullable=True)
    pe_underlying = db.Column(db.VARCHAR(200), nullable=True)
    pe_identifier = db.Column(db.VARCHAR(200), nullable=True)
    pe_open_interest = db.Column(db.Float, nullable=True)
    pe_changein_open_interest = db.Column(db.Float, nullable=True)
    pe_pchangein_open_interest = db.Column(db.Float, nullable=True)
    pe_total_traded_volume = db.Column(db.Float, nullable=True)
    pe_implied_volatility = db.Column(db.Float, nullable=True)
    pe_last_price = db.Column(db.Float, nullable=True)
    pe_change = db.Column(db.Float, nullable=True)
    pe_pchange = db.Column(db.Float, nullable=True)
    pe_total_buy_quantity = db.Column(db.Float, nullable=True)
    pe_total_sell_quantity = db.Column(db.Float, nullable=True)
    pe_bid_qty = db.Column(db.Float, nullable=True)
    pe_bidprice = db.Column(db.Float, nullable=True)
    pe_ask_qty = db.Column(db.Float, nullable=True)
    pe_ask_price = db.Column(db.Float, nullable=True)
    pe_underlying_value = db.Column(db.Float, nullable=True)
    # formulea fields
    ce_intrinsic_value = db.Column(db.Float, nullable=True)
    ce_time_value = db.Column(db.Float, nullable=True)
    pe_intrinsic_value = db.Column(db.Float, nullable=True)
    pe_time_value = db.Column(db.Float, nullable=True)
    # absolute_price
    absolute_price = db.Column(db.BigInteger, nullable=True)
    ce_open = db.Column(db.Float, nullable=True)
    pe_open = db.Column(db.Float, nullable=True)
    ce_high = db.Column(db.Float, nullable=True)
    pe_high = db.Column(db.Float, nullable=True)
    ce_low = db.Column(db.Float, nullable=True)
    pe_low = db.Column(db.Float, nullable=True)
    ce_close = db.Column(db.Float, nullable=True)
    pe_close = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.VARCHAR(100), nullable=True)
    