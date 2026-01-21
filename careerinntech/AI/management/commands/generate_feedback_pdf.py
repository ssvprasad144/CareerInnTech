from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from AI.views import _build_question_answer_pairs
from AI.models import InterviewSession, InterviewMessage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import textwrap
import os
import json


def draw_paragraph(c, text, x, y, wrap_width=95, leading=14):
    for line in textwrap.wrap(text or '', width=wrap_width):
        c.drawString(x, y, line)
        y -= leading
        if y < inch:
            c.showPage()
            y = A4[1] - inch
    return y


class Command(BaseCommand):
    help = 'Generate feedback PDF for a given interview session id and save to careerinntech/docs/'

    def add_arguments(self, parser):
        parser.add_argument('session_id', type=int, help='InterviewSession id')

    def handle(self, *args, **options):
        session_id = options['session_id']
        try:
            session = InterviewSession.objects.get(id=session_id)
        except InterviewSession.DoesNotExist:
            raise CommandError(f'Session {session_id} not found')

        # Attempt to load feedback data from session messages via services.generate_feedback if needed
        from AI.services import generate_feedback

        raw = generate_feedback(session)
        try:
            feedback = json.loads(raw)
        except Exception:
            feedback = {}

        qa_pairs = _build_question_answer_pairs(session)

        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs')
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f'feedback_{session_id}.pdf')

        c = canvas.Canvas(out_file, pagesize=A4)
        width, height = A4
        x = inch
        y = height - inch

        def draw_heading(text):
            nonlocal y
            c.setFont('Helvetica-Bold', 14)
            c.drawString(x, y, text)
            y -= 0.3 * inch

        def draw_par(text, indent=0):
            nonlocal y
            c.setFont('Helvetica', 10)
            for line in textwrap.wrap(text or '', width=95):
                c.drawString(x + indent, y, line)
                y -= 0.18 * inch
                if y < inch:
                    c.showPage()
                    y = height - inch

        draw_heading('AI Interview Feedback')
        draw_par(f'Session ID: {session_id}')
        draw_par(f"Overall Score: {feedback.get('overall_score', '--')}%")
        draw_par(f"Verdict: {feedback.get('verdict_title', 'Interview Completed')}")
        draw_par(feedback.get('verdict_summary', ''))

        if qa_pairs:
            y -= 0.1 * inch
            draw_heading('Question-wise Answers')
            for idx, pair in enumerate(qa_pairs, start=1):
                draw_par(f'Q{idx}: {pair.get("question")}', indent=0)
                draw_par(f'A{idx}: {pair.get("answer")}', indent=12)

        y -= 0.2 * inch
        draw_heading('Detailed Feedback')
        draw_par(feedback.get('detailed_feedback', ''))
        draw_par(f"Final Verdict: {feedback.get('final_verdict', '')}")

        c.showPage()
        c.save()

        self.stdout.write(self.style.SUCCESS(f'Wrote feedback PDF: {out_file}'))
