from tradeapp.services.service import NSELive
from tradeapp import app
nse_live = NSELive()


def option_chain_scheduler():
    with app.app_context():
        print("scheduler")
        nse_live.option_chain_indices("NIFTY")