from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase
from accounts.tests.factories import UserFactory
from assessment.api.resources.question_set import QuestionSetResource
from assessment.models import QuestionSet
from assessment.tests import QuizFactory, QuestionSetFactory
from courses.tests.factories import EnrollmentFactory
from uberlearner.urls import v1_api


class QuestionSetValidationTests(ResourceTestCase):
    def setUp(self):
        self.quiz = QuizFactory.create()
        self.post_data = {
            'quiz': self.quiz.get_resource_uri(),
            'points_per_question': 1
        }
        self.question_set_list_uri = reverse('api_dispatch_list', kwargs={
            'resource_name': QuestionSetResource._meta.resource_name,
            'api_name': v1_api.api_name
        })
        return super(QuestionSetValidationTests, self).setUp()

    def tearDown(self):
        self.quiz.course.instructor.delete()  # cascade
        return super(QuestionSetValidationTests, self).tearDown()

    def test_that_model_validation_carries_through(self):
        self.post_data['title'] = 'really long title; ' * 1000
        response = self.api_client.post(
            self.question_set_list_uri,
            data=self.post_data,
            authentication=self.create_basic(self.quiz.course.instructor.username, UserFactory._plain_text_password)
        )
        self.assertHttpBadRequest(response)
        content = self.deserialize(response)
        self.assertIn('questionSets', content)
        self.assertIn('title', content['questionSets'])

    def test_that_required_fields_cannot_be_absent(self):
        del self.post_data['points_per_question']
        response = self.api_client.post(
            self.question_set_list_uri,
            data=self.post_data,
            authentication=self.create_basic(self.quiz.course.instructor.username, UserFactory._plain_text_password)
        )
        self.assertHttpBadRequest(response)
        content = self.deserialize(response)
        self.assertIn('questionSets', content)
        self.assertIn('pointsPerQuestion', content['questionSets'])


class QuestionSetPermissionTests(ResourceTestCase):
    def setUp(self):
        self.question_set = QuestionSetFactory.create()
        self.quiz = self.question_set.quiz
        self.course = self.quiz.course
        self.post_data = {
            'quiz': self.quiz.get_resource_uri(),
            'points_per_question': 1
        }
        self.question_set_list_uri = reverse('api_dispatch_list', kwargs={
            'resource_name': QuestionSetResource._meta.resource_name,
            'api_name': v1_api.api_name
        })
        self.random_user = UserFactory.create()
        return super(QuestionSetPermissionTests, self).setUp()

    def tearDown(self):
        self.random_user.delete()
        self.quiz.course.instructor.delete()

    def _get_credentials(self, user):
        return self.create_basic(user.username, UserFactory._plain_text_password)

    def _http_method(self, method=None, **kwargs):
        if method is None:
            raise ValueError('Some action has to be performed on the quiz endpoint')
        if not hasattr(self.api_client, method):
            raise ValueError('Illegal http method attempted on the quiz endpoint')

        if 'authentication' in kwargs and kwargs['authentication'] is not None:
            kwargs['authentication'] = self._get_credentials(kwargs['authentication'])

        pre_creation_count = QuestionSet.objects.count()
        response = getattr(self.api_client, method)(**kwargs)
        post_creation_count = QuestionSet.objects.count()

        return response, pre_creation_count, post_creation_count

    def _create(self, data=None, **kwargs):
        data = data or self.post_data
        return self._http_method(method='post', uri=self.question_set_list_uri, data=data, **kwargs)

    def _read(self, question_set, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='get', uri=question_set.get_resource_uri(), **kwargs)

    def _read_list(self, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='get', uri=self.question_set_list_uri, **kwargs)

    def _update(self, question_set, data_update={}, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        if 'data' in kwargs:
            del kwargs['data']
        return self._http_method(method='put', uri=question_set.get_resource_uri(), data=data_update, **kwargs)

    def _delete(self, question_set, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='delete', uri=question_set.get_resource_uri(), **kwargs)

    def test_that_authorized_users_can_create_question_sets(self):
        response, pre_count, post_count = self._create(authentication=self.course.instructor)
        self.assertHttpCreated(response)
        self.assertEqual(pre_count + 1, post_count)

    def test_that_authorized_users_can_read_question_sets(self):
        response, pre_count, post_count = self._read(authentication=self.course.instructor,
                                                     question_set=self.question_set)
        self.assertHttpOK(response)
        content = self.deserialize(response)
        self.assertEqual(self.question_set.id, content['id'])

    def test_that_authorized_users_can_update_question_sets(self):
        response, pre_count, post_count = self._update(data_update={
            'title': 'another title'
        }, question_set=self.question_set, authentication=self.course.instructor)
        question_set = QuestionSet.objects.get(id=self.question_set.id)
        self.assertHttpAccepted(response)
        self.assertEqual(pre_count, post_count)
        self.assertEqual(question_set.title, 'another title')

    def test_that_authorized_users_can_delete_question_sets(self):
        response, pre_count, post_count = self._delete(question_set=self.question_set,
                                                       authentication=self.course.instructor)
        self.assertHttpAccepted(response)
        self.assertEqual(pre_count, post_count + 1)

    def test_that_unauthorized_users_cannot_create_question_sets(self):
        response, pre_count, post_count = self._create(authentication=self.random_user)
        self.assertHttpUnauthorized(response)
        self.assertEqual(pre_count, post_count)

    def test_that_unauthorized_users_cannot_read_question_sets(self):
        response, pre_count, post_count = self._read(question_set=self.question_set, authentication=None)
        self.assertHttpUnauthorized(response)

    def test_that_unauthorized_users_cannot_update_question_sets(self):
        pre_update_title = QuestionSet.objects.get(id=self.question_set.id).title
        response, pre_count, post_count = self._update(data_update={
            'title': 'another title'
        }, question_set=self.question_set, authentication=self.random_user)
        self.assertHttpUnauthorized(response)
        post_update_title = QuestionSet.objects.get(id=self.question_set.id).title
        self.assertEqual(pre_update_title, post_update_title)

    def test_that_unauthorized_users_cannot_delete_question_sets(self):
        response, pre_count, post_count = self._delete(question_set=self.question_set, authentication=self.random_user)
        self.assertHttpUnauthorized(response)
        self.assertEqual(pre_count, post_count)

    def test_that_instructors_can_only_list_question_sets_from_their_courses(self):
        another_question_set = QuestionSetFactory.create()
        self.assertNotEqual(another_question_set.quiz.course.id, self.course.id)
        response, pre_count, post_count = self._read_list(authentication=self.course.instructor)
        self.assertValidJSONResponse(response)
        content = self.deserialize(response)
        self.assertEqual(content['meta']['totalCount'], 1)
        self.assertEqual(len(content['objects']), 1)
        self.assertEqual(content['objects'][0]['id'], self.question_set.id)

    def test_that_students_can_only_list_question_sets_from_their_enrollments(self):
        enrollment = EnrollmentFactory.create()
        enrolled_course = enrollment.course
        enrolled_student = enrollment.student
        enrolled_question_set = QuestionSetFactory.create(quiz__course=enrolled_course)
        self.assertNotEqual(enrolled_course, self.course)
        response, pre_count, post_count = self._read_list(authentication=enrolled_student)
        self.assertValidJSONResponse(response)
        content = self.deserialize(response)
        self.assertEqual(content['meta']['totalCount'], 1)
        self.assertEqual(len(content['objects']), 1)
        self.assertEqual(content['objects'][0]['id'], enrolled_question_set.id)