# Create your views here.
from django.shortcuts import render_to_response
from django.core import serializers
from djangoconf.shard.models import *
from django.http import HttpResponse, HttpResponseServerError

def monitor(request):
    return render_to_response("index.html")

def shards(request):
    objects = []
    json_serializer = serializers.get_serializer("json")()
    json = None
     
    try:
        objs = ShardConf.objects.all();    
        json = json_serializer.serialize(objs, ensure_ascii=False) 
    except RuntimeError, e:
        json = json_serializer.serialize(e, ensure_ascii=False) 

    return HttpResponse(json, mimetype='text/javascript')

