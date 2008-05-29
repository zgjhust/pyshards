# Copyright (C) 2008 Devin Venable 
from django.db import models

class ShardConf(models.Model):
    id = models.IntegerField(primary_key=True)
    pid = models.IntegerField(null=True, blank=True)
    capacity_MB = models.IntegerField(null=True, blank=True)
    current_MB = models.IntegerField(null=True, blank=True)
    full = models.BooleanField(null=True)
    user = models.CharField(null=True,maxlength=100)
    password = models.CharField(null=True,maxlength=100)
    host = models.CharField(null=True,maxlength=100)
    database = models.CharField(null=True,maxlength=100)
    def __str__(self):
        return self.host 
    def notifyFull(self, full):
        if self.full and full == False:
            self.full = full
            self.save()
        elif self.full == False and full:
            self.full = full
            self.save()
    def notifyShardSize(self, size):
        if self.current_MB != size:
            self.current_MB = size
            self.save()
    class Meta:
        db_table = 'shard'
    class Admin:
        list_display = ('id', 'pid','user', 'host', 'capacity_MB','current_MB', 'full','database' )
        list_filter = ('id', 'pid', 'user', 'host', 'capacity_MB','current_MB', 'full','database')
        ordering = ('id',)
        

class VShardConf(models.Model):
    id = models.IntegerField(primary_key=True)
    pid = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.id
    class Meta:
        db_table = 'vshard'
    class Admin:
        list_display = ('id', 'pid' )
        list_filter = ('pid',)
        ordering = ('id',)