from jinja2 import Environment, FileSystemLoader
import os

def render_template(source_template_path: str, template_params: dict) -> str:
    """
    Render a Jinja2 template with given parameters
    
    Args:
        source_template_path: Full path to the template file
        template_params: Dictionary containing template parameters
    
    Returns:
        str: Rendered template output
    """
    template_dir = os.path.dirname(source_template_path)
    template_file = os.path.basename(source_template_path)
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    return template.render(template_params)
