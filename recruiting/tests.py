from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock, mock_open
import json

from .utils import (
    extract_text_from_pdf,
    compute_match,
    normalize_skill,
    compute_match_v2
)
from .ai_client import parse_cv_text, analyze_meeting_transcript
from .models import Application
from projects.models import Project


class CVExtractionTestCase(TestCase):
    """Tests para las utilidades de extracción de texto de CVs"""

    @patch('recruiting.utils.PdfReader')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test')
    def test_extract_text_from_pdf_success(self, mock_file, mock_pdf_reader):
        """Test: Extracción exitosa de texto desde PDF"""
        # Mock del PdfReader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto del CV\nNombre: Juan Pérez"
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # Ejecutar
        result = extract_text_from_pdf("fake_path.pdf")

        # Verificar
        self.assertIn("Texto del CV", result)
        self.assertIn("Juan Pérez", result)

    @patch('recruiting.utils.PdfReader')
    @patch('builtins.open', side_effect=Exception("Error de lectura"))
    def test_extract_text_from_pdf_error(self, mock_file, mock_pdf_reader):
        """Test: Manejo de error en extracción de PDF"""
        result = extract_text_from_pdf("invalid.pdf")
        self.assertEqual(result, "")


class SkillMatchingTestCase(TestCase):
    """Tests para el matching de habilidades"""

    def test_compute_match_exact_match(self):
        """Test: Match perfecto de habilidades"""
        required = ["Python", "Django", "React"]
        candidate = ["python", "django", "react"]
        
        score = compute_match(required, candidate)
        self.assertEqual(score, 100.0)

    def test_compute_match_partial_match(self):
        """Test: Match parcial de habilidades"""
        required = ["Python", "Django", "React", "AWS"]
        candidate = ["Python", "Django"]
        
        score = compute_match(required, candidate)
        self.assertEqual(score, 50.0)  # 2 de 4 = 50%

    def test_compute_match_no_match(self):
        """Test: Sin match de habilidades"""
        required = ["Python", "Django"]
        candidate = ["Java", "Spring"]
        
        score = compute_match(required, candidate)
        self.assertEqual(score, 0.0)

    def test_compute_match_empty_inputs(self):
        """Test: Manejo de inputs vacíos"""
        self.assertEqual(compute_match([], ["Python"]), 0.0)
        self.assertEqual(compute_match(["Python"], []), 0.0)
        self.assertEqual(compute_match([], []), 0.0)

    def test_normalize_skill_synonyms(self):
        """Test: Normalización de sinónimos de habilidades"""
        self.assertEqual(normalize_skill("React.js"), "react")
        self.assertEqual(normalize_skill("ReactJS"), "react")
        self.assertEqual(normalize_skill("React JS"), "react")
        self.assertEqual(normalize_skill("C#"), "c#")
        self.assertEqual(normalize_skill("C Sharp"), "c#")
        self.assertEqual(normalize_skill(".NET"), ".net")
        self.assertEqual(normalize_skill("dotnet"), ".net")

    def test_normalize_skill_removes_special_chars(self):
        """Test: Eliminación de caracteres especiales"""
        result = normalize_skill("Python (avanzado)")
        self.assertNotIn("(", result)
        self.assertNotIn(")", result)

    def test_compute_fuzzy_match(self):
        """Test: Match difuso de habilidades"""
        required = ["Python", "Django", "React"]
        candidate = ["python", "django rest framework", "reactjs"]
        
        score = compute_match_v2(required, candidate)
        # Debería tener un buen match considerando sinónimos y match parcial
        self.assertGreater(score, 50.0)


class AIClientTestCase(TestCase):
    """Tests para el cliente de IA de recruiting"""

    @patch('recruiting.ai_client.client')
    def test_parse_cv_text_success(self, mock_client):
        """Test: Parsing exitoso de CV con IA"""
        # Mock de respuesta de OpenAI
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "full_name": "Juan Pérez",
            "emails": ["juan@example.com"],
            "phones": ["+56912345678"],
            "skills": {
                "hard": ["Python", "Django", "React"],
                "soft": ["Trabajo en equipo", "Comunicación"]
            },
            "education": [{"degree": "Ingeniería en Informática"}],
            "experience": [{"company": "Tech Corp", "position": "Developer"}],
            "links": ["https://github.com/juanperez"],
            "languages": ["Español", "Inglés"]
        })
        mock_client.chat.completions.create.return_value = mock_response

        # Ejecutar
        cv_text = "Juan Pérez\nDesarrollador Python con 5 años de experiencia"
        result = parse_cv_text(cv_text)

        # Verificar
        self.assertEqual(result["full_name"], "Juan Pérez")
        self.assertIn("juan@example.com", result["emails"])
        self.assertIn("Python", result["skills"]["hard"])

    @patch('recruiting.ai_client.client')
    def test_analyze_meeting_transcript_success(self, mock_client):
        """Test: Análisis exitoso de transcript de reunión"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "project_summary": "Sistema de gestión de inventario",
            "required_skills": ["Python", "Django", "PostgreSQL"],
            "functional_requirements": [
                {
                    "id": "FR1",
                    "title": "Login de usuarios",
                    "description": "Sistema de autenticación",
                    "complexity": "media",
                    "estimated_hours": 8
                }
            ],
            "non_functional_requirements": [
                {"id": "NFR1", "description": "Alta disponibilidad"}
            ],
            "assumptions": ["Se usará servidor cloud"],
            "risks": ["Cambios de requerimientos"],
            "total_estimated_hours": 100,
            "hourly_rate": 50,
            "estimated_cost": 5000
        })
        mock_client.chat.completions.create.return_value = mock_response

        # Ejecutar
        transcript = "Cliente necesita sistema de inventario con login"
        result = analyze_meeting_transcript(transcript, hourly_rate=50)

        # Verificar
        self.assertIn("project_summary", result)
        self.assertIn("required_skills", result)
        self.assertEqual(len(result["required_skills"]), 3)
        self.assertEqual(result["hourly_rate"], 50)


class ApplicationMatchingTestCase(APITestCase):
    """Tests para el matching de aplicaciones con proyectos"""

    def setUp(self):
        self.candidate = User.objects.create_user(
            username='matching_candidate',
            password='test123',
            email='matching@test.com'
        )
        self.project = Project.objects.create(
            title="Proyecto Django",
            description="Sistema web con Django y React",
            required_skills=["Python", "Django", "React", "PostgreSQL"]
        )

    def test_application_match_calculation(self):
        """Test: Cálculo de match entre candidato y proyecto"""
        # Crear aplicación con skills del candidato
        application = Application.objects.create(
            candidate=self.candidate,
            project=self.project,
            extracted={
                "full_name": "Candidato Test",
                "skills": {
                    "hard": ["Python", "Django", "React"],
                    "soft": ["Trabajo en equipo"]
                }
            }
        )

        # Calcular match
        candidate_skills = application.extracted.get("skills", {}).get("hard", [])
        required_skills = self.project.required_skills
        
        match_score = compute_match(required_skills, candidate_skills)

        # Verificar (tiene 3 de 4 skills requeridas = 75%)
        self.assertEqual(match_score, 75.0)


class SkillNormalizationEdgeCasesTestCase(TestCase):
    """Tests para casos edge de normalización de skills"""

    def test_normalize_skill_with_dots(self):
        """Test: Normalización de skills con puntos"""
        # La función mantiene el punto en algunos casos como node.js
        self.assertIn(normalize_skill("Node.js").lower(), ["node.js", "nodejs"])
        self.assertIn(normalize_skill("Vue.js").lower(), ["vue.js", "vuejs"])

    def test_normalize_skill_special_cases(self):
        """Test: Casos especiales de normalización"""
        # MAUI detection
        self.assertEqual(normalize_skill(".NET MAUI"), "maui")
        self.assertEqual(normalize_skill(".NET con MAUI"), "maui")
        
        # .NET variations
        self.assertEqual(normalize_skill(".NET Core"), ".net")
        self.assertEqual(normalize_skill("ASP.NET"), ".net")

    def test_normalize_skill_empty_input(self):
        """Test: Manejo de input vacío"""
        self.assertEqual(normalize_skill(""), "")
        self.assertEqual(normalize_skill(None), "")
        self.assertEqual(normalize_skill("   "), "")
