#encoding: utf-8

import json
from hollowman.filters import BaseFilter


class ForcePullFilter(BaseFilter):

    def __init__(self, ctx):
        super(ForcePullFilter, self).__init__(ctx)

    def run(self, request):
        
        if request.is_json and request.data:
            data = request.get_json()

            if self.is_single_app(data):
                original_app_dict = json.loads(self.get_original_app(request).to_json())
                original_app_dict.update(data)

                if 'labels' in original_app_dict and ('hollowman.disable_forcepull' in original_app_dict['labels']):
                    value = False
                else:
                    value = True

                original_app_dict['container']['docker']["forcePullImage"] = value

                request.data = json.dumps(original_app_dict)

        return request