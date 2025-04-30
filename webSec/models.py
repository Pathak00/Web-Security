import json
from django.db import models

class VulnerabilityScanReport(models.Model):
    username = models.CharField(max_length=255)
    pdf_response = models.TextField() 
    domain=models.CharField(max_length=255)# Stores JSON as a string
    severity = models.TextField()  # Stores JSON as a string
    created_at = models.DateTimeField(auto_now_add=True) 
    # Timestamp for when the report was created

    def set_pdf_response(self, data):
        """Serializes and sets the PDF response as JSON string."""
        self.pdf_response = json.dumps(data)

    def get_pdf_response(self):
        """Deserializes and returns the PDF response as a Python object."""
        return json.loads(self.pdf_response)

    def set_severity(self, data):
        """Serializes and sets the severity as JSON string."""
        self.severity = json.dumps(data)
    
    def get_severity(self):
        """Deserializes and returns the severity as a Python object."""
        return json.loads(self.severity)

    def __str__(self):
        return f"Report for {self.username} -{self.domain}- {self.created_at}"
