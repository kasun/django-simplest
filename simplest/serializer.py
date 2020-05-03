from django.db import models
from django.core import serializers


class Serializer:
    def __init__(self, query_set, fields=None, include_id=True):
        self.query_set = query_set
        self.fields = fields
        self.include_id = include_id

    def serialize(self):
        if isinstance(self.query_set, models.Model):
            data = serializers.serialize('python', [self.query_set], self.fields)[0]
            data_out = data['fields'].copy()
            if self.include_id:
                data_out['id'] = data['pk']
        else:
            data_out = []
            data = serializers.serialize('python', self.query_set, fields=self.fields)
            for da in data:
                d = da['fields'].copy()
                if self.include_id:
                    d['id'] = da['pk']

                data_out.append(d)

        return data_out
