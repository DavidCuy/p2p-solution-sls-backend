from http import HTTPStatus

from core_api.responses import api_response
from core_decorators import requester_patch
from core_utils.utils import get_logger, get_body
from core_decorators.logs import lambda_logger
from playhouse.shortcuts import model_to_dict

from core_db.models import P2Ptransaction
from datetime import datetime
import core_aws.eventbridge
import uuid

requester_patch()
LOGGER = get_logger()


@lambda_logger(logger=LOGGER)
def lambda_handler(event: dict, _):
    records = event.get("Records")
    if records is None:
        LOGGER.info("No records founded")
        return {
            "error": True,
            "message": "No records founded"
        }
    
    trxs = []
    event_details = {
        "name": "Send Notification",
        "details": None
    }
    for record in records:
        body = get_body(record)
        LOGGER.info(f'{20 * '*'}  Processing banking request  {20 * '*'}')

        trx_reg = P2Ptransaction.get_by_id(body.get('id', None))
        LOGGER.info(trx_reg)
        mock_resp = {
            'trx_id': str(uuid.uuid4())
        }
        trx_status = 'done'
        resp_body = {
            "error": False,
            "message": "OK"
        }

        if 'error' in body:
            mock_resp = {
                'error': True,
                'message': 'Somenthing goes wrong at bank services'
            }
            trx_status = 'failure'
            resp_body["error"] = True
            resp_body["message"] = "Something goes wrong"
        else:
            resp_body["trx"] = trx_reg
            mock_resp["source"] = trx_reg.source_id
            mock_resp["dest"] = trx_reg.dest_id
            mock_resp["amount"] = trx_reg.amount
            mock_resp["timestamp"] = datetime.now().isoformat()

        trx_reg.status = trx_status
        trx_reg.save()

        trx_obj = model_to_dict(trx_reg)

        resp_body["trx_details"] = mock_resp

        event_details['details'] = {
            'trx_id': mock_resp['trx_id'],
            'payload_request': trx_obj,
            'details': mock_resp
        }

        status = core_aws.eventbridge.put_event(
            event_name=event_details['name'],
            event_input=event_details['details']
        )

        
        trxs.append({
            'input': trx_obj,
            'output': resp_body,
            'eb_status': status
        })
    return api_response({
        "message": "OK",
        "transactions": trxs
    }, HTTPStatus.OK)