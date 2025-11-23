from peewee import SqliteDatabase
from database_model import db, Component, GearConfiguration, UserPreference
from utils import generate_uuid
import logging
import datetime

logger = logging.getLogger(__name__)

DATABASE_NAME = "gear_calc.db"

def initialize_db():
    """Initialize the database connection and create tables."""
    database = SqliteDatabase(DATABASE_NAME)
    db.initialize(database)
    db.connect()
    _create_tables()
    logger.info("Database initialized and tables created.")

def _create_tables():
    with db:
        db.create_tables([Component, GearConfiguration, UserPreference], safe=True)

def get_user_preferences():
    """Get the user preferences. Create default if not exists."""
    try:
        return UserPreference.get_by_id(1)
    except UserPreference.DoesNotExist:
        return UserPreference.create(min_ratio=1.0, max_ratio=5.0)

def update_user_preferences(min_ratio, max_ratio):
    """Update user preferences."""
    prefs = get_user_preferences()
    prefs.min_ratio = min_ratio
    prefs.max_ratio = max_ratio
    prefs.save()
    return prefs

def add_component(name, type, teeth, speed=None, comments=None):
    """Add a new component to the database."""
    try:
        component = Component.create(
            id=generate_uuid(),
            name=name,
            type=type,
            speed=speed,
            teeth=teeth,
            comments=comments if comments and comments != "None" else None
        )
        return component
    except Exception as e:
        logger.error(f"Error adding component: {e}")
        raise

def update_component(component_id, name, type, teeth, speed=None, comments=None):
    """Update an existing component."""
    try:
        query = Component.update(
            name=name,
            type=type,
            speed=speed,
            teeth=teeth,
            comments=comments if comments and comments != "None" else None
        ).where(Component.id == component_id)
        return query.execute()
    except Exception as e:
        logger.error(f"Error updating component: {e}")
        raise

def get_components(type=None):
    """Get all components, optionally filtered by type."""
    try:
        if type:
            return list(Component.select().where(Component.type == type))
        return list(Component.select())
    except Exception as e:
        logger.error(f"Error getting components: {e}")
        return []

def get_component(component_id):
    """Get a single component by ID."""
    try:
        return Component.get(Component.id == component_id)
    except Exception as e:
        logger.error(f"Error getting component: {e}")
        return None

def delete_component(component_id):
    """Delete a component by ID."""
    try:
        query = Component.delete().where(Component.id == component_id)
        return query.execute()
    except Exception as e:
        logger.error(f"Error deleting component: {e}")
        raise

def add_configuration(name, front_component_id, rear_component_id, comments=None):
    """Add a new gear configuration."""
    try:
        config = GearConfiguration.create(
            id=generate_uuid(),
            name=name,
            front_component_id=front_component_id,
            rear_component_id=rear_component_id,
            comments=comments if comments and comments != "None" else None
        )
        return config
    except Exception as e:
        logger.error(f"Error adding configuration: {e}")
        raise

def update_configuration(config_id, name, front_component_id, rear_component_id, comments=None):
    """Update an existing gear configuration."""
    try:
        query = GearConfiguration.update(
            name=name,
            front_component_id=front_component_id,
            rear_component_id=rear_component_id,
            comments=comments if comments and comments != "None" else None
        ).where(GearConfiguration.id == config_id)
        return query.execute()
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise

def get_configurations():
    """Get all gear configurations."""
    try:
        return list(GearConfiguration.select())
    except Exception as e:
        logger.error(f"Error getting configurations: {e}")
        return []

def get_configuration(config_id):
    """Get a single configuration by ID."""
    try:
        return GearConfiguration.get(GearConfiguration.id == config_id)
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        return None

def delete_configuration(config_id):
    """Delete a configuration by ID."""
    try:
        query = GearConfiguration.delete().where(GearConfiguration.id == config_id)
        return query.execute()
    except Exception as e:
        logger.error(f"Error deleting configuration: {e}")
        raise
