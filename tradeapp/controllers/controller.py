from tradeapp.dto.dtos import api
from flask_restx import Resource, reqparse
from tradeapp.services.service import *

api = api
# option_chain_CRUD = OptionChainCRUD()
nse_live = NSELive()

# ?symbol=NIFTY

@api.route('/')
class NSEOptionChainLive(Resource):
    @api.doc('fetch nse data')
    # @api.marshal_list_with(_dtotemp, envelope='data',mask=False)
    def get(self):
        """This is API 1"""
        return nse_live.option_chain_indices("NIFTY")
    
@api.route('/derivatives')
class NSEDerivatives(Resource):
    @api.doc('fetch derivatives')
    # @api.marshal_list_with(_dtotemp, envelope='data',mask=False)
    def get(self):
        """This is API 1"""
        return nse_live.derivatives("NIFTY")
    
    
@api.route('/get-all')
class FetchAll(Resource):
    @api.doc('Get all from DB')
    def get(self):
        """This is API 1"""
        return nse_live.get_all()
    
@api.route('/ce-pe-formulea')
class CePeFormulea(Resource):
    @api.doc('Get ce strike price and pe strike price')
    def get(self):
        """This is API 1"""
        return nse_live.ce_pe_formulea()


@api.route('/co_po_chart')
class CoPoChart(Resource):
    @api.doc('Get co po bar chart')
    def get(self):
        """This is API 1"""
        return nse_live.co_po_chart()

    def post(self):
        """This is API 1"""
        return nse_live.co_po_chart()

@api.route('/co_po_change_chart')
class CoPoChangeChart(Resource):
    @api.doc('Get co po change bar chart')
    def get(self):
        """This is API 1"""
        return nse_live.co_po_change_chart()

    def post(self):
        """This is API 1"""
        return nse_live.co_po_change_chart()


@api.route('/multi_strike_line_chart')
class MultiStrike(Resource):
    @api.doc('Get multi strike line chart')
    def get(self):
        """This is API 1"""
        return nse_live.multi_strike_line_chart()

    def post(self):
        """This is API 1"""
        return nse_live.multi_strike_line_chart()


@api.route('/get_strike_price')
class GetStrike(Resource):
    def post(self):
        """This is API 1"""
        return nse_live.get_price_for_multi_strike()


@api.route('/cumulative_oi_chart')
class CumulativeChart(Resource):
    @api.doc('Get cumulative OI, OI Change chart')
    def get(self):
        """This is API 1"""
        return nse_live.cumulative_change_chart()

    def post(self):
        """This is API 1"""
        return nse_live.cumulative_change_chart()

@api.route('/max_pain_chart')
class MaxPainChart(Resource):
    @api.doc('Get max pain chart')
    def get(self):
        """This is API 1"""
        return nse_live.max_pain_chart()

    def post(self):
        """This is API 1"""
        return nse_live.max_pain_chart()