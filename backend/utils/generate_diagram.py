from langchain_core.runnables.graph import MermaidDrawMethod

def generate_diagram(app):
    # Generate the PNG image
    png_data = app.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API,
    )

    # Define the file path
    file_path = "backend/schema_diagram/workflow_diagram.png"

    # Save the image locally
    with open(file_path, "wb") as f:
        f.write(png_data)

    print(f"Workflow diagram saved as {file_path}")