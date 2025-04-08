from crewai.tools import BaseTool
from .client import Client as LinkedinClient
from .database import Database
import re

class LinkedInTool(BaseTool):
    name: str = "LinkedIn Pharmacy Technician Search Tool"
    description: str = (
        "Search for Pharmacy Technicians on LinkedIn based on specific criteria and store results in the database"
    )

    def _run(self, criteria: str) -> str:
        linkedin_client = LinkedinClient()
        
        # Ensure we're searching for Pharmacy Technicians
        if "pharmacy technician" not in criteria.lower():
            criteria = f"pharmacy technician, {criteria}"
        
        # Add US location if not specified
        if "united states" not in criteria.lower() and "us " not in criteria.lower():
            criteria = f"{criteria}, United States"
        
        # Search LinkedIn with the combined criteria
        try:
            people = linkedin_client.find_people(criteria)  
            
            if not people:
                return "No Pharmacy Technician profiles found matching the criteria."
            
            # Store data in PostgreSQL
            db = Database()
            stored_profiles = []
            
            for person in people:
                # Extract basic info
                candidate_id = db.insert_candidate(
                    person['name'],
                    person['position'],
                    person['location'],
                    person['profile_link']
                )
                
                # Extract pharmacy-specific information
                experience = self._extract_experience(person['position'])
                certifications = self._extract_certifications(person['position'])
                skills = self._extract_skills(person['position'])
                workplace = self._extract_workplace(person['position'])
                
                # Store the details
                db.insert_candidate_details(
                    candidate_id,
                    experience,
                    certifications,
                    skills,
                    workplace,
                    0.0  # Initial score, will be updated by analyzer agent
                )
                
                stored_profiles.append(person['name'])
            
            db.close()
            
            # Format for crew output
            formatted_people = self._format_publications_to_text(people)
            summary = f"Successfully found and stored {len(stored_profiles)} Pharmacy Technician profiles matching the criteria: {criteria}"
            
            return f"{summary}\n\n{formatted_people}"
            
        except Exception as e:
            return f"Error searching LinkedIn: {str(e)}"
        finally:
            linkedin_client.close()
            
            
    def _format_publications_to_text(self, people):
        result = ["\n".join([
            f"Profile #{i+1}:",
            f"Name: {p['name']}",
            f"Position: {p['position']}",
            f"Location: {p['location']}",
            f"Profile Link: {p['profile_link']}",
            f"Experience: {self._extract_experience(p['position'])}",
            f"Certifications: {self._extract_certifications(p['position'])}",
            f"Likely Skills: {self._extract_skills(p['position'])}",
            f"Workplace Type: {self._extract_workplace(p['position'])}"
        ]) for i, p in enumerate(people)]
        result = "\n\n".join(result)

        return result
        
    def _extract_experience(self, position):
        """Extract potential experience info from position text"""
        experience = "Not specified"
        years_keywords = ["year", "yr", "years"]
        
        for keyword in years_keywords:
            if keyword in position.lower():
                # Extract the experience using regex to find patterns like "5 years"
                match = re.search(r'(\d+)\s*(?:year|yr|years)', position.lower())
                if match:
                    experience = f"{match.group(1)} years of experience"
                    break
        
        return experience

    def _extract_certifications(self, position):
        """Extract potential certification info from position text"""
        certifications = []
        cert_keywords = {
            "CPhT": "Certified Pharmacy Technician (CPhT)",
            "PTCB": "Pharmacy Technician Certification Board (PTCB) certified",
            "ExCPT": "Exam for the Certification of Pharmacy Technicians (ExCPT)",
            "NHA": "National Healthcareer Association certified",
            "certified": "Certified Pharmacy Technician"
        }
        
        for keyword, full_cert in cert_keywords.items():
            if keyword.lower() in position.lower():
                certifications.append(full_cert)
        
        return ", ".join(certifications) if certifications else "Not specified"

    def _extract_skills(self, position):
        """Extract potential skills from position text"""
        skills = []
        skill_keywords = {
            "retail": "retail pharmacy",
            "hospital": "hospital pharmacy",
            "compounding": "medication compounding",
            "inventory": "inventory management",
            "billing": "insurance billing",
            "sterile": "sterile compounding",
            "IV": "IV preparation",
            "customer service": "customer service",
            "EMR": "electronic medical records"
        }
        
        for keyword, skill in skill_keywords.items():
            if keyword.lower() in position.lower():
                skills.append(skill)
        
        # Add default pharmacy skills
        if not skills:
            skills = ["medication dispensing", "pharmacy operations", "prescription processing"]
        
        return ", ".join(skills)

    def _extract_workplace(self, position):
        """Extract potential workplace info from position text"""
        workplaces = []
        workplace_keywords = {
            "hospital": "Hospital",
            "retail": "Retail Pharmacy",
            "clinic": "Clinical Setting",
            "pharmacy": "Pharmacy",
            "drugstore": "Drugstore",
            "CVS": "CVS Pharmacy",
            "Walgreens": "Walgreens",
            "Rite Aid": "Rite Aid",
            "Walmart": "Walmart Pharmacy",
            "long-term care": "Long-term Care Facility",
            "LTC": "Long-term Care Facility"
        }
        
        for keyword, workplace in workplace_keywords.items():
            if keyword.lower() in position.lower():
                workplaces.append(workplace)
        
        return ", ".join(workplaces) if workplaces else "Not specified"