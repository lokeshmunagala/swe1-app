from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question, Choice
from django.urls import reverse

# Create your tests here.


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(choice_text, question_id):
    return Choice.objects.create(question=question_id, choice_text=choice_text)


class QuestionIndexViewTests(TestCase):
    def test_html_home_page(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)

    def test_html_detail_page(self):
        past_question = create_question(question_text="Present Question.", days=0)
        response = self.client.get(reverse("polls:detail", args=(past_question.id,)))
        self.assertEqual(response.status_code, 200)

    def test_html_result_page(self):
        past_question = create_question(question_text="Present Question.", days=0)
        time = past_question.was_published_recently()
        self.assertEqual(time, True)

    def test_html_vote_page(self):
        present_question = create_question(question_text="Present Question.", days=0)
        response = self.client.get(reverse("polls:vote", args=(present_question.id,)))
        self.assertEqual(response.status_code, 200)
        present_choice = create_choice(
            question_id=present_question, choice_text="Present Choice"
        )
        response = self.client.post(
            reverse("polls:vote", args=(present_question.id,)),
            {"choice": str(present_choice.id)},
        )
        self.assertEqual(response.status_code, 302)

    def test_text(self):
        past_question = create_question(question_text="Past Question.", days=0)
        response = self.client.get(reverse("polls:results", args=(past_question.id,)))
        self.assertEqual(response.status_code, 200)

    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_two_past_questions(self):
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )
