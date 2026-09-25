# CareerInnTech

A full-stack career platform built with Django, PostgreSQL and OpenAI-powered interview features.

## What it does

CareerInnTech combines career profiles, skills, projects, college and placement information, and AI-assisted interview preparation in one web application.

### Highlights

- Django-based full-stack architecture
- PostgreSQL-backed application data
- Authentication, signup and session security
- AI mock interview workflows using OpenAI
- Interview-session ownership and CSRF protections
- Production-oriented configuration with Gunicorn and WhiteNoise
- Modular Django apps for colleges, placements, projects, skills and AI features

## Tech Stack

**Backend:** Python, Django  
**Database:** PostgreSQL  
**AI:** OpenAI API  
**Frontend:** HTML, CSS, JavaScript, Django Templates  
**Deployment:** Gunicorn, WhiteNoise, Render

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

## Local Development

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

Configure environment variables such as the Django secret key and OpenAI API key before using AI features.

## Engineering Notes

Recent work includes strengthening authentication and interview-session security, enforcing CSRF protection, and improving production browser/session security.

## Portfolio

GitHub: https://github.com/ssvprasad144

Built as a hands-on full-stack engineering project focused on production-minded web development and AI integration.
