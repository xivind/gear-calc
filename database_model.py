from peewee import *
import datetime

# We will initialize the database proxy here, but bind it later in database_manager
db = Proxy()

class BaseModel(Model):
    class Meta:
        database = db

class Component(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    type = CharField() # Chainring or Cassette
    speed = IntegerField(null=True) # e.g. 11 for 11-speed
    teeth = TextField() # JSON string or comma-separated list of teeth
    comments = TextField(null=True)

class GearConfiguration(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    front_component_id = ForeignKeyField(Component, backref='front_configs')
    rear_component_id = ForeignKeyField(Component, backref='rear_configs')
    comments = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

class UserPreference(BaseModel):
    """User preferences for gear ratio color coding.

    This is designed as a singleton - only one record (ID=1) should exist.
    The application always fetches/creates this single record.
    """
    id = AutoField(primary_key=True)
    min_ratio = FloatField(default=0.8)
    max_ratio = FloatField(default=3.2)
