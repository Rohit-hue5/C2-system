from typing import Dict, Any
from jinja2 import Template
import json

class ReportGenerator:
    def generate_html(self, analysis: Dict) -> str:
        """Generate HTML report"""
        template = """
        <html>
        <body>
            <h1>Analysis Report</h1>
            <p>Hash: {{ analysis.hash }}</p>
            <p>Score: {{ analysis.score }}</p>
            <h2>Behaviors</h2>
            <ul>{% for behavior in analysis.details.behavior %}<li>{{ behavior }}</li>{% endfor %}</ul>
        </body>
        </html>
        """
        t = Template(template)
        return t.render(analysis=analysis)
