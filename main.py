from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import business_logic
import database_manager
from logger import logger
from seed_data import seed_database
import uvicorn

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

def health_check():
    """Test database connectivity and write healthcheck status"""
    try:
        # Test database connectivity with a simple query
        from database_model import Component
        Component.select().limit(1).execute()
        with open("status.txt", "w", encoding='utf-8') as file:
            file.write("ok")
        logger.info("Health check passed")
        return True
    except Exception as error:
        logger.error(f"Health check failed: {error}")
        with open("status.txt", "w", encoding='utf-8') as file:
            file.write("error")
        return False

@app.on_event("startup")
def startup_event():
    database_manager.initialize_db()
    seed_database()
    database_manager.cleanup_orphaned_configurations()
    logger.info("Performing startup health check...")
    health_check()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    configs = business_logic.get_landing_page_data()
    return templates.TemplateResponse("index.html", {"request": request, "configs": configs})

@app.get("/calculator", response_class=HTMLResponse)
async def calculator_page(request: Request):
    chainrings = business_logic.get_component_options("Chainring")
    cassettes = business_logic.get_component_options("Cassette")
    return templates.TemplateResponse("gear_ratio.html", {
        "request": request, 
        "chainrings": chainrings, 
        "cassettes": cassettes,
        "config": None
    })

@app.get("/preferences", response_class=HTMLResponse)
async def get_preferences(request: Request):
    prefs = database_manager.get_user_preferences()
    return templates.TemplateResponse("preferences.html", {"request": request, "preferences": prefs})

@app.post("/preferences")
async def save_preferences(
    min_ratio: float = Form(...),
    max_ratio: float = Form(...)
):
    database_manager.update_user_preferences(min_ratio, max_ratio)
    return RedirectResponse(url="/?msg=Preferences saved successfully", status_code=303)

@app.get("/calculator/{config_id}", response_class=HTMLResponse)
async def calculator_detail(request: Request, config_id: str):
    details = business_logic.get_configuration_details(config_id)
    if not details:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    chainrings = business_logic.get_component_options("Chainring")
    cassettes = business_logic.get_component_options("Cassette")
    
    return templates.TemplateResponse("gear_ratio.html", {
        "request": request,
        "chainrings": chainrings,
        "cassettes": cassettes,
        "config": details["config"],
        "selected_front": details["front_component"].id,
        "selected_rear": details["rear_component"].id,
        "gear_tables": details["gear_tables"],
        "total_range": details["total_range"]
    })

@app.post("/calculate-preview", response_class=HTMLResponse)
async def calculate_preview(
    request: Request,
    front_component_id: str = Form(...),
    rear_component_id: str = Form(...)
):
    gear_tables = business_logic.calculate_from_components(front_component_id, rear_component_id)
    return templates.TemplateResponse("partials/calculation_results.html", {
        "request": request,
        "gear_tables": gear_tables
    })

@app.post("/calculator")
async def save_configuration(
    name: str = Form(...),
    front_component_id: str = Form(...),
    rear_component_id: str = Form(...),
    comments: str = Form(None),
    config_id: str = Form(None)
):
    try:
        if config_id:
            business_logic.update_configuration(config_id, name, front_component_id, rear_component_id, comments)
            msg = "Configuration updated successfully"
        else:
            business_logic.create_configuration(name, front_component_id, rear_component_id, comments)
            msg = "Configuration created successfully"
        return RedirectResponse(url=f"/?msg={msg}", status_code=303)
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

@app.delete("/calculator/{config_id}")
async def delete_configuration(config_id: str):
    try:
        business_logic.delete_configuration(config_id)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deleting configuration: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/components", response_class=HTMLResponse)
async def components_page(request: Request):
    chainrings = business_logic.get_components_by_type("Chainring")
    cassettes = business_logic.get_components_by_type("Cassette")
    return templates.TemplateResponse("components.html", {
        "request": request,
        "chainrings": chainrings,
        "cassettes": cassettes,
        "edit_component": None
    })

@app.get("/components/{component_id}", response_class=HTMLResponse)
async def edit_component_page(request: Request, component_id: str):
    chainrings = business_logic.get_components_by_type("Chainring")
    cassettes = business_logic.get_components_by_type("Cassette")
    component = business_logic.get_component(component_id)
    
    return templates.TemplateResponse("components.html", {
        "request": request,
        "chainrings": chainrings,
        "cassettes": cassettes,
        "edit_component": component
    })

@app.post("/components")
async def save_component(
    name: str = Form(...),
    type: str = Form(...),
    teeth: str = Form(...),
    speed: int = Form(None),
    comments: str = Form(None),
    component_id: str = Form(None)
):
    try:
        business_logic.save_component(name, type, teeth, speed, comments, component_id)
        msg = "Component updated successfully" if component_id else "Component added successfully"
        return RedirectResponse(url=f"/components?msg={msg}", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving component: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/components/{component_id}")
async def delete_component(component_id: str):
    try:
        business_logic.delete_component(component_id)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deleting component: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
