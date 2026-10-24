"""
Project Configuration & Metadata
EFREI Paris - Data Storytelling Dashboard 2026
"""

STUDENT_NAME = "Alexandre Morin"
STUDENT_ID = "20230873"
STUDENT_GROUP = "DAI"
COURSE_NAME = "Data Visualization & Storytelling"
PROFESSOR_NAME = "Mano Joseph Mathew"
PROFESSOR_EMAIL = "mano.mathew@efrei.fr"

APP_TITLE = "The Care Deficit: Mapping France's Medical Deserts"
APP_SUBTITLE = "How the demographic cliff and geographic inequality threaten French healthcare access"
APP_HASHTAGS = "#EFREIDataStories2026 #EFREIParis #DataStorytelling #OpenData #Streamlit"

ARCHIVE_NAME = f"StApp26_{STUDENT_ID}_{STUDENT_NAME.split()[-1].upper()}_{STUDENT_GROUP}.zip"

# Official DREES Thresholds
APL_CRITICAL_THRESHOLD = 2.5   # Under 2.5 consultations/year/inhabitant = ZIP code under-dense ("Désert Médical")
APL_NATIONAL_TARGET = 4.0      # Satisfactory level of primary care access

# Dataset Metadata
DATASET_TITLE = "Accessibilité Potentielle Localisée (APL) aux professionnels de santé (Médecins Généralistes)"
DATASET_PRODUCER = "Ministère du Travail, de la Santé et des Solidarités (DREES)"
DATASET_PORTAL = "data.gouv.fr (French Open Data)"
DATASET_PORTAL_URL = "https://www.data.gouv.fr/datasets/accessibilite-potentielle-localisee-apl-aux-professionnels-de-sante"
DATASET_LICENSE = "Licence Ouverte / Open Licence 2.0 (Etalab)"
DATASET_URL = "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/530_l-accessibilite-potentielle-localisee-apl/attachments/indicateur_d_apl_aux_medecins_generalistes_xlsx"
