from unittest import TestCase, mock
from unittest.mock import MagicMock
from core_api.utils import get_body
from .lambda_function import lambda_handler


def mock_get_parameter(param_name, *args, **kwargs):
    if param_name == _XML_HEADER_PARAMETER_NAME:
        return {"dNumTim": "12559367", "dEst": "001", "dPunExp": "001"}
    if param_name == _RUC_TRANSMITTER:
        return {"dRucEm": 80021477, "dDVEmi": 3}
    if param_name == constant.PARAMETER_ACCOUNTS_ADJUSTMENT:
        return '{ "adjustment":{ "interest":{ "account":41080150, "tax_payable":21070101 }, "feeReceivedAccount":{ "account":41080119, "tax_payable":21070101 }, "penalties":{ "account":41080151, "tax_payable":21070101 } } }'
    return None


patch_transaction = {
    "returnCode": 0,
    "returnStatus": "SUCCESS"
}


def return_response_mock(status_code, body):
    mock = MagicMock()
    mock.status_code = status_code
    mock.data = body
    return mock


@mock.patch('core_aws.ssm.get_parameter', side_effect=mock_get_parameter)
class Test(TestCase):
    def setUp(self) -> None:
        """Set up data to use in every test case"""

        self.event = {
            "detail": {
                "total_amount": 7212,
                "tax_amount": 656,
                "tax_rate": 10,
                "period": 21,
                "client_id": CLIENT_ID,
                "pay_invoice_type": PayInvoiceType.CASH.value,
                "account_id": "test",
                "transaction_affected": ['test'],
                "account_holder_key": "test"
            }
        }

        self.bad_event = {
            "detail": {
                "total_amount": 7212,
                "tax_rate": "abs",
                "period": 21,
                "client_id": CLIENT_ID,
                "pay_invoice_type": PayInvoiceType.CASH.value
            }
        }

    def test_compensatory(self, *_, **__):
        response = lambda_handler(self.event, None)
        got = get_body(response)
        want = "<rDE><DE><gOpeDE><iTipEmi>1</iTipEmi></gOpeDE><gTimb><iTiDE>1</iTiDE><dNumTim>12559367</dNumTim><dEst>001</dEst><dPunExp>001</dPunExp><dNumDoc>777780</dNumDoc></gTimb><gDatGralOpe><dFeEmiDE>2023-11-29T00:00:00</dFeEmiDE><gOpeCom><iTipTra>2</iTipTra><iTImp>1</iTImp><cMoneOpe>PYG</cMoneOpe></gOpeCom><gEmis><dRucEm>80021477</dRucEm><dDVEmi>3</dDVEmi><iTipCont>2</iTipCont></gEmis><gDatRec><iNatRec>2</iNatRec><iTiOpe>2</iTiOpe><cPaisRec>PRY</cPaisRec><dNomRec>GUSTAVO GAVILAN</dNomRec><iTipIDRec>1</iTipIDRec><dNumIDRec>6088987</dNumIDRec></gDatRec></gDatGralOpe><gDtipDE><gCamFE><iIndPres>2</iIndPres></gCamFE><gCamItem><dCodInt>REV0003</dCodInt><dDesProSer>Intereses moratorios</dDesProSer><dCantProSer>1</dCantProSer><gValorItem><dPUniProSer>7212</dPUniProSer><dTotBruOpeItem>7212</dTotBruOpeItem><gValorRestaItem><dDescItem>0</dDescItem><dAntGloPreUniIt>0</dAntGloPreUniIt><dTotOpeItem>7212</dTotOpeItem></gValorRestaItem></gValorItem><gCamIVA><iAfecIVA>1</iAfecIVA><dTasaIVA>10</dTasaIVA><dBasGravIVA>6556</dBasGravIVA><dLiqIVAItem>656</dLiqIVAItem></gCamIVA></gCamItem><gCamCond><iCondOpe>1</iCondOpe><gPaConEIni><iTiPago>1</iTiPago><dMonTiPag>7212</dMonTiPag><cMoneTiPag>PYG</cMoneTiPag></gPaConEIni></gCamCond></gDtipDE></DE></rDE>"
        self.maxDiff = None
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(want, got)

    def test_bad_request(self, *_, **__):
        response = lambda_handler(self.bad_event, None)
        self.assertEqual(response['statusCode'], 422)
