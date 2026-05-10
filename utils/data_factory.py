from faker import Faker
import random

fake=Faker()

def generate_employee():
  return{
    'first_name':fake.first_name(),
    'last_name':fake.last_name(),
    'employee_id':str(random.randint(1000,9999)),
    'username':fake.user_name()+str(random.randint(10,99)),
    'password':'Test@1234',
    'job_title':random.choice(['Software Engineer','AI Engineer','Business Analyst','HR Manager']),
  }


def  generate_leave_date():
  return{
    'frome_date':'2025-12-01',
    'to_date':'2025-12-03',
  }

