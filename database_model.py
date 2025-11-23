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
    type = CharField() # Chainring, Cog, Cassette
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

class UserPreference(BaseModel): # Inherit from BaseModel for consistency
    min_ratio = FloatField(default=1.0)
    max_ratio = FloatField(default=5.0)
