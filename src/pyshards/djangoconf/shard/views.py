# Create your views here.
from django.shortcuts import render_to_response
from django.core import serializers
from djangoconf.shard.models import *
from django.http import HttpResponse, HttpResponseServerError
 
from djangoconf.loader import DjangoShardLoader 
 

def monitor(request):
    topshards = DjangoShardLoader()
    
    tops = []
    
    for shard in topshards:
        bucket = []
                        
        while shard != None:
            
            whole = shard.capacity_MB or 1
            part = shard.current_MB 
            
            shard.per = (part * 100) / whole
            shard.red = 55 + (shard.per * 2)              
            shard.green = 255 - (shard.per * 2)
            
            if shard.green > 200:
                shard.text = 0
            else:
                shard.text = 255
             
            bucket.append(shard)                        
            shard = shard.next
        
        tops.append(bucket)
    
    return render_to_response("index.html", { "shards": tops  })

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

