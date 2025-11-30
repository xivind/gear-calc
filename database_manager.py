from peewee import SqliteDatabase
from database_model import db, Component, GearConfiguration, UserPreference
from utils import generate_uuid, empty_to_none
import logging
import datetime
import os

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/gear_calc.db")
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def initialize_db():
    """Initialize the database connection and create tables."""
    database = SqliteDatabase(DATABASE_PATH)
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
        return UserPreference.create(min_ratio=0.8, max_ratio=3.2)

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
            comments=empty_to_none(comments)
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
            comments=empty_to_none(comments)
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

def get_configurations_using_component(component_id):
    """Get all configurations that use a specific component."""
    try:
        configs = GearConfiguration.select().where(
            (GearConfiguration.front_component_id == component_id) |
            (GearConfiguration.rear_component_id == component_id)
        )
        return list(configs)
    except Exception as e:
        logger.error(f"Error getting configurations using component: {e}")
        return []

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
            comments=empty_to_none(comments)
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
            comments=empty_to_none(comments)
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

def cleanup_orphaned_configurations():
    """Delete configurations that reference non-existent components."""
    try:
        # Get all component IDs that exist
        existing_component_ids = set(c.id for c in Component.select(Component.id))

        # Get all configurations with their raw foreign key values
        all_configs = GearConfiguration.select()
        deleted_count = 0

        for config in all_configs:
            # Access the raw foreign key ID fields (not the related objects)
            front_id = config.front_component_id_id
            rear_id = config.rear_component_id_id

            # Check if the referenced components exist
            if front_id not in existing_component_ids or rear_id not in existing_component_ids:
                logger.info(f"Deleting orphaned configuration: {config.id} (name: {config.name})")
                config.delete_instance()
                deleted_count += 1

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} orphaned configuration(s)")

        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up orphaned configurations: {e}")
        return 0
