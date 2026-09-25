# CareerInnTech

> **Full-stack career platform with AI-powered interview workflows, secure authentication, and production-oriented Django architecture.**

**Developer:** SSVPrasad  
**Stack:** Django · PostgreSQL · OpenAI · JavaScript · Gunicorn · WhiteNoise

## Product Overview

CareerInnTech brings career profiles, skills, projects, college and placement information, and AI-assisted interview preparation into one web application.

The project is designed around practical full-stack engineering concerns: structured backend modules, database-backed features, authenticated sessions, AI integration, CSRF protection, and production deployment.

## What I Built

- Full-stack Django application with modular domain apps
- PostgreSQL-backed career, college, placement, project and skills data
- Authentication, signup and session handling
- AI-powered mock interview workflows using OpenAI
- Interview-session ownership and CSRF protections
- Production configuration with Gunicorn and WhiteNoise
- Deployment-oriented environment configuration

## Engineering Highlights

**Backend architecture**  
Organized Django functionality into focused applications for AI, colleges, placements, projects, skills and core functionality.

**AI integration**  
Connected application workflows to OpenAI for AI-assisted interview experiences.

**Security**  
Implemented authentication/session protections, CSRF handling and interview-session ownership checks.

**Production**  
Configured the application for hosted deployment with Gunicorn, WhiteNoise and environment-based secrets.

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python · Django |
| Database | PostgreSQL |
| AI | OpenAI API |
| Frontend | HTML · CSS · JavaScript · Django Templates |
| Production | Gunicorn · WhiteNoise · Render |

## Run Locally

```bash
git clone https://github.com/ssvprasad144/CareerInnTech.git
cd CareerInnTech

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Configure the required environment variables, including the Django secret key and OpenAI API key, before using AI functionality.

## Project Structure

```text
CareerInnTech/
├── ai/
├── college/
├── core/
├── placements/
├── projects/
├── skills/
├── careerinntech/
├── static/
├── templates/
└── manage.py
```

## Developer

**SSVPrasad**  
Full-Stack Developer · AI Integration · Backend Engineering

GitHub: https://github.com/ssvprasad144
