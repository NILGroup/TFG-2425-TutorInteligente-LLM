from llm.llm import ask
import markdown
import pdfkit
import datetime
import os

class ReportAgent:
    def __init__(self, knowledge, student, context_manager):
        self.knowledge = knowledge
        self.student = student
        self.context_manager = context_manager
        self.events = [] # (timestamp, nombre_evento, descripcion_evento)

    def generate_content(self):
        context = (
            "Eres el tutor de un estudiante que se encuentra en un entorno de realidad virtual diseñado para entrenar situaciones de emergencia radiológica. "
            "Tu tarea es redactar un informe claro, estructurado y en formato Markdown sobre el desempeño del estudiante durante el nivel actual.\n\n"
        )

        # Añadir contexto específico del nivel, tareas y conversaciones
        context += self.context_manager.generate_level_info_context()
        context += self.context_manager.generate_tasks_context()
        context += self.context_manager.generate_conversation_context()

        # Añadir eventos relevantes registrados durante la partida
        context += "\nAdemás, has registrado los siguientes eventos destacables:\n"
        for timestamp, name, desc in self.events:
            context += f"- **{name}** ({timestamp}): {desc}\n"

        context += "Ten en cuenta que has intervenido para ayudar al estudiante en los casos que has indicado."
        # Instrucciones sobre formato y estructura
        context += (
            "\nTu respuesta debe estar escrita en formato Markdown y contener los siguientes elementos:\n"
            "- Título: Informe de Desempeño del Estudiante en el Nivel ...\n"
            "- Secciones obligatorias:\n"
            "  1. Descripción del Nivel\n"
            "  2. Progreso del Estudiante\n"
            "  3. Eventos Destacables. No tienes porqué limitarte a los eventos listados previamente. Puedes generar nuevos a partir de toda la información que tienes, como las conversaciones.\n"
            "  4. Recomendaciones\n"
            "  5. Conclusión\n\n"
            "Sé claro, conciso y profesional. Utiliza listas o negritas cuando sea útil para organizar mejor la información. No olvides incluir enter cuando sea necesario.\n"
            "Importante: tu objetivo es evaluar el desempeño del estudiante. No incluyas comentarios sobre tu propia actuación como tutor ni hagas recomendaciones que no estén relacionadas directamente con el alumno."
        )
        answer = ask(context)

        return answer
    
    def generate_report(self):
        content = self.generate_content()
        html_body = markdown.markdown(content)
        html_full = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 2em; }}
                h1, h2, h3 {{ color: #333; }}
                code {{ background: #f2f2f2; padding: 2px 4px; border-radius: 4px; }}
                blockquote {{ color: #555; margin-left: 1em; padding-left: 1em; border-left: 4px solid #ccc; }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # Crear el PDF desde string
        ruta_wkhtmltopdf = os.getenv("WKHTMLTOPDF_PATH", r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe') 
        config = pdfkit.configuration(wkhtmltopdf=ruta_wkhtmltopdf)
        curr_time = datetime.datetime.now()
        formatted_time = curr_time.strftime("%Y_%m_%d_%H_%M_%S")
        no_spaces_title = self.knowledge.level_name.replace(" ", "_")
        pdfkit.from_string(html_full, f"./output-reports/{formatted_time}_{no_spaces_title}.pdf", configuration=config)

        
        
    def add_event(self, timestamp, title, description):
        self.events.append((timestamp, title, description))

