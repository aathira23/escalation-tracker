
from app.database import SessionLocal
from app.models.client import Client
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.project import Project
from app.models.skill import Skill
from app.services.auth_service import AuthService

def seed_data():
    db = SessionLocal()
    try:
        print("Seeding Clients...")
        clients_data = [
            {"name": "ACME Corp", "email_domain": "acmecorp.com", "industry": "retail"},
            {"name": "TechStart", "email_domain": "techstart.io", "industry": "technology"},
            {"name": "GlobalRetail", "email_domain": "globalretail.com", "industry": "retail"},
            {"name": "Example Corp", "email_domain": "example.com", "industry": "general"},
            {"name": "Victim Company", "email_domain": "victim-company.com", "industry": "finance"},
        ]
        
        for c_data in clients_data:
            existing = db.query(Client).filter(Client.email_domain == c_data["email_domain"]).first()
            if not existing:
                client = Client(
                    name=c_data["name"],
                    email_domain=c_data["email_domain"],
                    industry=c_data["industry"]
                )
                db.add(client)
                print(f"- Added {c_data['name']}")
            else:
                print(f"- {c_data['name']} already exists")
        
        print("\nSeeding Departments & Projects...")
        depts_projects = {
            "Engineering": ["API Platform", "Mobile App", "Infrastructure"],
            "Operations": ["Billing Support", "Account Management"],
            "Product": ["User Experience", "Feature Requests"]
        }
        
        dept_objects = {}
        for dept_name, proj_names in depts_projects.items():
            dept = db.query(Department).filter(Department.name == dept_name).first()
            if not dept:
                dept = Department(name=dept_name)
                db.add(dept)
                db.flush()
                print(f"- Added Department: {dept_name}")
            dept_objects[dept_name] = dept
            
            for proj_name in proj_names:
                proj = db.query(Project).filter(Project.name == proj_name).first()
                if not proj:
                    proj = Project(name=proj_name, department_id=dept.id)
                    db.add(proj)
                    print(f"  - Added Project: {proj_name}")
        
        print("\nSeeding Skills...")
        skills_list = ["technical", "api", "billing", "finance", "mobile", "design", "security"]
        skill_objects = {}
        for skill_name in skills_list:
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.add(skill)
                db.flush()
                print(f"- Added Skill: {skill_name}")
            skill_objects[skill_name] = skill

        print("\nSeeding Users (Resolvers)...")
        resolvers = [
            {"email": "john.doe@support.com", "name": "John Doe", "role": UserRole.MANAGER, "tags": ["technical", "api"], "dept": "Engineering", "project": "API Platform"},
            {"email": "jane.smith@support.com", "name": "Jane Smith", "role": UserRole.VIEWER, "tags": ["billing", "finance"], "dept": "Operations", "project": "Billing Support"},
            {"email": "alice.dev@support.com", "name": "Alice Developer", "role": UserRole.VIEWER, "tags": ["technical", "mobile"], "dept": "Engineering", "project": "Mobile App"},
            {"email": "mike.prod@support.com", "name": "Mike Product", "role": UserRole.VIEWER, "tags": ["billing", "finance"], "dept": "Operations", "project": "Billing Support"},
        ]
        
        for r_data in resolvers:
            user = AuthService.get_user_by_email(db, r_data["email"])
            if not user:
                user = AuthService.create_user(
                    db, 
                    r_data["email"], 
                    "password123", 
                    r_data["name"], 
                    r_data["role"], 
                    expertise_tags=r_data["tags"]
                )
                print(f"- Added {r_data['name']}")
            else:
                print(f"- {r_data['name']} already exists")
            
            # Link to skills
            for tag in r_data["tags"]:
                if tag in skill_objects and skill_objects[tag] not in user.skills:
                    user.skills.append(skill_objects[tag])
            
            # Link to project
            if "project" in r_data:
                proj = db.query(Project).filter(Project.name == r_data["project"]).first()
                if proj and proj not in user.projects:
                    user.projects.append(proj)
                
        db.commit()
        print("\nSeeding Complete!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
