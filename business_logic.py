import database_manager
import json
import logging

logger = logging.getLogger(__name__)

def calculate_gear_ratios(front_teeth, rear_teeth, preferences=None):
    """
    Calculate gear ratios for given front and rear teeth.
    Returns a list of dictionaries, one for each front chainring.
    """
    results = []
    
    sorted_rear = sorted(rear_teeth, reverse=True)
    
    for front in front_teeth:
        gears = []
        prev_ratio = 0
        
        for i, rear in enumerate(sorted_rear):
            ratio = round(front / rear, 3)
            
            change_pct = 0
            if prev_ratio > 0:
                change_pct = round(((ratio - prev_ratio) / prev_ratio) * 100, 1)
            
            # Determine status based on preferences
            status = "normal"
            if preferences:
                min_r = preferences.min_ratio
                max_r = preferences.max_ratio
                range_span = max_r - min_r
                warning_buffer = range_span * 0.1 # 10% buffer
                
                if ratio < min_r or ratio > max_r:
                    status = "poor"
                elif (ratio < min_r + warning_buffer) or (ratio > max_r - warning_buffer):
                    status = "warning"
                else:
                    status = "optimal"

            gears.append({
                "rear_tooth": rear,
                "ratio": ratio,
                "gear_num": i + 1,
                "change_pct": change_pct if i > 0 else None,
                "status": status
            })
            prev_ratio = ratio
            
        # Calculate total range
        if gears:
            min_ratio = gears[0]["ratio"]
            max_ratio = gears[-1]["ratio"]
            total_range = calculate_total_range_value([front], rear_teeth)
        else:
            total_range = 0
        
        results.append({
            "front_tooth": front,
            "total_range": total_range,
            "gears": gears
        })
    
    return results

def parse_teeth(teeth_val):
    """
    Parse teeth input into a list of integers.
    Handles:
    - List of ints/strings
    - JSON string
    - Comma-separated string
    - Single int/string
    """
    if isinstance(teeth_val, list):
        return [int(t) for t in teeth_val]
    
    if isinstance(teeth_val, str):
        try:
            # Try JSON first
            parsed = json.loads(teeth_val)
            if isinstance(parsed, list):
                return [int(t) for t in parsed]
            return [int(parsed)]
        except json.JSONDecodeError:
            # Try comma-separated
            return [int(t.strip()) for t in teeth_val.split(',')]
            
    # Single integer or other type
    return [int(teeth_val)]

def calculate_total_range_value(front_teeth, rear_teeth):
    """
    Calculate the total gear range percentage.
    Range = (Max Ratio / Min Ratio) * 100
    Max Ratio = Max Front / Min Rear
    Min Ratio = Min Front / Max Rear
    """
    if not front_teeth or not rear_teeth:
        return 0
        
    max_front = max(front_teeth)
    min_front = min(front_teeth)
    max_rear = max(rear_teeth)
    min_rear = min(rear_teeth)
    
    if min_rear == 0 or max_rear == 0:
        return 0
        
    max_ratio = max_front / min_rear
    min_ratio = min_front / max_rear
    
    if min_ratio == 0:
        return 0
        
    return round((max_ratio / min_ratio) * 100)


def get_landing_page_data():
    """Get data for the landing page (list of configurations)."""
    configs = database_manager.get_configurations()
    data = []
    for config in configs:
        try:
            front = config.front_component_id
            rear = config.rear_component_id
            
            front_teeth = parse_teeth(front.teeth)
            rear_teeth = parse_teeth(rear.teeth)
            
            total_range = calculate_total_range_value(front_teeth, rear_teeth)
            
            data.append({
                "id": config.id,
                "name": config.name,
                "front_name": front.name,
                "rear_name": rear.name,
                "total_range": total_range,
                "comments": config.comments,
                "created_at": config.created_at.strftime("%Y-%m-%d %H:%M")
            })
        except Exception as e:
            logger.warning(f"Skipping config {config.id} due to error: {e}")
            continue
            
    return data

def get_component_options(component_type):
    """Get component options for dropdowns."""
    components = database_manager.get_components(type=component_type)
    options = []
    for comp in components:
        options.append({
            "value": comp.id,
            "text": f"{comp.name} ({comp.speed}s)" if comp.speed else comp.name,
            "teeth": json.loads(comp.teeth)
        })
    return options

def create_configuration(name, front_id, rear_id, comments=None):
    """Create a new gear configuration."""
    return database_manager.add_configuration(name, front_id, rear_id, comments)

def update_configuration(config_id, name, front_id, rear_id, comments=None):
    """Update an existing gear configuration."""
    return database_manager.update_configuration(config_id, name, front_id, rear_id, comments)

def save_component(name, type, teeth_str, speed=None, comments=None, component_id=None):
    """Create or update a component."""
    # Validate teeth input (comma separated integers)
    try:
        # Handle if teeth_str is already a list (e.g. from JSON payload)
        if isinstance(teeth_str, list):
            teeth_list = [int(t) for t in teeth_str]
        else:
            teeth_list = [int(t.strip()) for t in teeth_str.split(',')]

        # Validate all teeth values are positive integers
        for tooth in teeth_list:
            if tooth <= 0:
                raise ValueError("Teeth values must be positive integers.")

        teeth_json = json.dumps(teeth_list)
    except ValueError as e:
        if "positive integers" in str(e):
            raise e
        raise ValueError("Invalid teeth format. Must be comma-separated whole numbers (integers) only, no decimals.")

    # Validate speed if provided
    if speed is not None:
        if speed <= 0:
            raise ValueError("Speed must be a positive integer.")
        if speed != len(teeth_list):
            raise ValueError(f"Speed value ({speed}) must match the number of teeth values ({len(teeth_list)}).")

    if component_id:
        return database_manager.update_component(component_id, name, type, teeth_json, speed, comments)
    else:
        return database_manager.add_component(name, type, teeth_json, speed, comments)

def get_component(component_id):
    """Get a single component."""
    comp = database_manager.get_component(component_id)
    if comp:
        # Parse teeth for frontend
        comp.teeth_list = json.loads(comp.teeth)
        # Format teeth string for edit form
        comp.teeth_str = ", ".join(map(str, comp.teeth_list))
    return comp

def get_components_by_type(component_type):
    """Get all components of a specific type."""
    return database_manager.get_components(type=component_type)

def get_configuration_details(config_id):
    """Get details for a specific configuration including calculated ratios."""
    config = database_manager.get_configuration(config_id)
    if not config:
        return None
    
    front = config.front_component_id
    rear = config.rear_component_id
    
    # Ensure teeth are parsed as lists of integers
    try:
        front_teeth = parse_teeth(front.teeth)
        rear_teeth = parse_teeth(rear.teeth)
    except Exception as e:
        logger.error(f"Error parsing teeth for config {config_id}: {e}")
        return None # Return None if teeth parsing fails
    
    # Get user preferences
    preferences = database_manager.get_user_preferences()

    # Calculate ratios with preferences
    gear_tables = calculate_gear_ratios(front_teeth, rear_teeth, preferences)
    
    # Calculate overall total range for the configuration
    total_range = calculate_total_range_value(front_teeth, rear_teeth)
    
    return {
        "config": config,
        "front_component": front,
        "rear_component": rear,
        "gear_tables": gear_tables,
        "total_range": total_range
    }

def delete_component(component_id):
    """Delete a component and all configurations that use it."""
    # First, find and delete all configurations using this component
    configs = database_manager.get_configurations_using_component(component_id)
    for config in configs:
        logger.info(f"Deleting configuration {config.name} (id: {config.id}) that uses component {component_id}")
        database_manager.delete_configuration(config.id)

    # Then delete the component itself
    return database_manager.delete_component(component_id)

def delete_configuration(config_id):
    return database_manager.delete_configuration(config_id)

def calculate_from_components(front_id, rear_id):
    """Calculate ratios based on component IDs."""
    front = get_component(front_id)
    rear = get_component(rear_id)

    if not front or not rear:
        return None

    # Get user preferences for color coding
    preferences = database_manager.get_user_preferences()

    return calculate_gear_ratios(front.teeth_list, rear.teeth_list, preferences)
