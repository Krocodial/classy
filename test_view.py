from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from django.contrib.auth.models import User
from classy.forms import loginform


class unAuthTests(TestCase):


    def setUp(self):
        user = User.objects.create(username='basic', is_staff=False)
        user.set_password('password')
        user.save()
        user = User.objects.create(username='staff', is_staff=True)
        user.set_password('staff_password')
        user.save()
        user = User.objects.create_superuser('super', 'xx@xx.com', 'super_password')
        user.save()        

        self.client = Client()

    def test_unauth_access(self):
        response = self.client.get(reverse('classy:index'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('classy:home'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:data'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:data') + '/1')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:uploader'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:search'))
        self.assertEqual(response.status_code, 302) 
        response = self.client.get(reverse('classy:modi'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:review'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:exceptions'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:log_list'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:download'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('classy:tutorial'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)

    def test_base_user_access(self):
        c = Client()
        response = c.post(reverse('classy:index'), {'username': 'basic', 'password': 'password'})
        response = c.get(reverse('classy:index'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:home'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:data'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:data') + '/1')
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:uploader'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:search'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:modi'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:review'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:exceptions'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:log_list'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:download'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:tutorial'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:user_logout'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:data'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)


    def test_staff_user_access(self):
        c = Client()
        
        response = c.post(reverse('classy:index'), {'username': 'staff', 'password': 'staff_password'})
        response = c.get(reverse('classy:index'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:home'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:data'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:data') + '/1')
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:uploader'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:search'))
        self.assertEqual(response.status_code, 200)
        response = c.post(reverse('classy:modi'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:review'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:exceptions'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:log_list'))
        self.assertEqual(response.status_code, 200)
        response = c.post(reverse('classy:download'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:tutorial'))
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('classy:user_logout'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:data'))
        self.assertEqual(response.status_code, 302)

    def test_super_user_access(self):
        c = Client()
    
        response = c.post(reverse('classy:index'), {'username': 'super', 'password': 'super_password'})
        response = c.get(reverse('classy:index'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:home'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:data'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:data') + '/1')
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:uploader'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:search'))
        self.assertEqual(response.status_code, 200)
        response = c.post(reverse('classy:modi'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:review'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:exceptions'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:log_list'))
        self.assertEqual(response.status_code, 200)
        response = c.post(reverse('classy:download'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('classy:tutorial'))
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        response = c.get(reverse('admin:login'))
        self.assertEqual(response.status_code, 302)


        response = c.get(reverse('classy:user_logout'))
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:data'))
        self.assertEqual(response.status_code, 302)





