from crewai_tools import BaseTool
from .database import Database

class DatabaseTool(BaseTool):
    name: str = "Database Management Tool"
    description: str = (
        "Tool for accessing and updating the pharmacy technician candidate database"
    )

    def _run(self, command: str) -> str:
        db = Database()
        try:
            if command.startswith("get_candidates"):
                limit = 100
                offset = 0
                if "limit=" in command:
                    limit = int(command.split("limit=")[1].split()[0])
                if "offset=" in command:
                    offset = int(command.split("offset=")[1].split()[0])
                candidates = db.get_candidates(limit, offset)
                return self._format_candidates(candidates)
            
            elif command.startswith("get_top_candidates"):
                limit = 10
                if "limit=" in command:
                    limit = int(command.split("limit=")[1].split()[0])
                candidates = db.get_top_candidates(limit)
                return self._format_candidates(candidates)
            
            elif command.startswith("get_candidate_by_id"):
                candidate_id = int(command.split("id=")[1].split()[0])
                candidate = db.get_candidate_by_id(candidate_id)
                return self._format_candidates([candidate]) if candidate else "Candidate not found"
            
            elif command.startswith("get_statistics"):
                stats = db.get_statistics()
                return self._format_statistics(stats)
            
            elif command.startswith("update_score"):
                # Example: update_score id=5 score=8.5
                parts = command.split()
                candidate_id = int([p for p in parts if p.startswith("id=")][0].split("=")[1])
                score = float([p for p in parts if p.startswith("score=")][0].split("=")[1])
                db.update_candidate_score(candidate_id, score)
                return f"Score updated for candidate {candidate_id} to {score}"
            
            elif command.startswith("add_outreach"):
                # Example: add_outreach id=5 template="..." strategy="..."
                cmd = command[len("add_outreach "):]
                id_part = cmd.split("template=")[0].strip()
                candidate_id = int(id_part.split("id=")[1].strip())
                template_part = cmd.split("template=")[1]
                if "strategy=" in template_part:
                    template = template_part.split("strategy=")[0].strip().strip('"')
                    strategy = template_part.split("strategy=")[1].strip().strip('"')
                else:
                    template = template_part.strip().strip('"')
                    strategy = "Standard outreach"
                
                db.insert_outreach_strategy(candidate_id, template, strategy)
                return f"Outreach strategy added for candidate {candidate_id}"
            
            else:
                return "Unknown command. Available commands: get_candidates, get_top_candidates, get_candidate_by_id, get_statistics, update_score, add_outreach"
        
        except Exception as e:
            return f"Database error: {str(e)}"
        finally:
            db.close()
            
    def _format_candidates(self, candidates):
        if not candidates:
            return "No candidates found."
            
        result = []
        for c in candidates:
            result.append("\n".join([
                f"Candidate ID: {c['id']}",
                f"Name: {c['name']}",
                f"Position: {c['position']}",
                f"Location: {c['location']}",
                f"Score: {c.get('score', 'Not scored')}",
                f"Experience: {c.get('experience', 'Not specified')}",
                f"Certifications: {c.get('certifications', 'Not specified')}",
                f"Skills: {c.get('skills', 'Not specified')}",
                f"Workplace: {c.get('workplace', 'Not specified')}",
                f"Profile Link: {c['profile_link']}"
            ]))
        return "\n\n".join(result)
    
    def _format_statistics(self, stats):
        return "\n".join([
            "Database Statistics:",
            f"Total Candidates: {stats['total_candidates']}",
            f"Average Score: {stats['average_score']:.2f}",
            f"Candidates with Certifications: {stats['with_certifications']}",
            f"Top Locations: {', '.join(stats['top_locations'])}",
            f"Top Workplaces: {', '.join(stats['top_workplaces'])}"
        ])