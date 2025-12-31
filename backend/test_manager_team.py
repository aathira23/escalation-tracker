
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.project import Project

def test_manager_visibility():
    db = SessionLocal()
    try:
        managers = db.query(User).filter(User.role == UserRole.MANAGER).all()
        for manager in managers:
            print(f"\nManager: {manager.full_name} ({manager.email})")
            project_ids = [p.id for p in manager.projects]
            project_names = [p.name for p in manager.projects]
            print(f"Projects: {project_names}")
            
            # Query like the router does
            query = db.query(User).join(User.projects).filter(Project.id.in_(project_ids))
            team = query.all()
            
            print(f"Team found ({len(team)}):")
            for member in team:
                member_projects = [p.name for p in member.projects]
                print(f"- {member.full_name} ({member.role}) | Projects: {member_projects}")
    finally:
        db.close()

if __name__ == "__main__":
    test_manager_visibility()
