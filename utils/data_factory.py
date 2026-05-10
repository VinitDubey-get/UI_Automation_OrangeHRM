import random
import logging
from faker import Faker

fake = Faker()
logger = logging.getLogger(__name__)


def generate_employee() -> dict:
    """Generate realistic random employee data for test use."""
    data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "username": fake.user_name() + str(random.randint(10, 99)),
        "password": "Test@1234",
        "job_title": random.choice([
            "Software Engineer", "QA Engineer",
            "HR Manager", "Business Analyst", "DevOps Engineer",
        ]),
    }
    logger.info(f"[DataFactory] Generated employee: {data['first_name']} {data['last_name']}")
    return data


def generate_vacancy_name() -> str:
    """Generate a unique vacancy name."""
    name = f"Test Vacancy {fake.word().capitalize()} {random.randint(100, 999)}"
    logger.info(f"[DataFactory] Generated vacancy name: {name}")
    return name