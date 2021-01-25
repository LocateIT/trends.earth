import polling2
from MISLAND.api import call_api

class Poller(object):
    execution_id = None
    DURATION = 30

    def __init__(self,execution_id):
        self.execution_id = execution_id

    def get_execution(self):
        return call_api(u'/api/v1/execution/{}'.format(self.execution_id), method='get', use_token=True)

    def poll(self):
        status = polling2.poll(lambda:self.get_execution(),check_success=self.is_finished,step=self.DURATION,poll_forever=True)
        return status

    @staticmethod
    def is_running(response):
        status = response.get('data',{}).get("status")
        return status == 'RUNNING'

    @staticmethod
    def is_finished(response):
        status = response.get('data',{}).get("status")
        return status == 'FINISHED'
        


