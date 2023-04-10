from enum import Enum
import os
import datetime
import random
from faker import Faker
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from account.models import Profile
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
os.environ.setdefault('SEED', '23')

        
            

model = Faker(int(os.environ.get("SEED")))



class Sentence(str):
    SIZES = [3, 5, 8, 11]
    def __init__(
        self,
        *args,
        num_words=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.num_words = num_words if num_words else random.choice(self.SIZES)
        self.sentence = model.sentence(nb_words=self.num_words, variable_nb_words=False)

    def __str__(self):
        return self.sentence

    def __repr__(self):
        return str(self)
        

class Paragraph(str):
    SIZES = [5, 8, 13]
    def __init__(
        self,
        *args,
        num_sentences=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.num_sentences = num_sentences if num_sentences is not None else random.choice(self.SIZES)
        self.sentences = []
        self._generate()

    def _generate(self):
        for c in range(self.num_sentences):
            self.sentences.append(Sentence())

    def __str__(self):
        sentences = [str(s) for s in self.sentences]
        return "\t" + ' '.join(sentences)

    def __repr__(self):
        return str(self)
    

class Article():
    def __init__(
        self,
        num,
        *args,
        has_title=False,
        has_quote=False,
        has_image=False,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.num = num
        self.title = model.bs().title() if has_title else None
        self.quote = None
        self.image = model.image(size=(256, 256)) if has_image else None
        self.paragraphs = []
        self._generate()

    def _generate(self):
        for c in range(self.num):
            self.paragraphs.append(Paragraph())

    def __str__(self):
        pars = [str(par) for par in self.paragraphs]
        return "\n".join(pars)

    

def user_gen(count=1, password='onefullsend'):
    for i in range(count):
        kwargs = {
            'password': make_password(password),
            'first_name': model.first_name(),
            'last_name': model.last_name(),
            'username': model.user_name(),
            'email': model.email()
        }
        yield make_user(**kwargs)



def post_gen(count=25, min_paragraphs=2, max_paragraphs=6, since='-2y', future=False):
    for i in range(count):
        article = Article(
            random.randint(min_paragraphs, max_paragraphs),
            has_title=True,
            has_quote=False,
            has_image=False
        )
        kwargs = {
            'title': article.title,
            'author': random.choice(User.objects.filter(is_active=True)),
            'publish': model.past_datetime() if not future else model.date_time_this_year(),
            'body': str(article),
            'slug': slugify(article.title)
        }
        kwargs['status'] = Post.Status.DRAFT if is_future(kwargs['publish']) else Post.Status.PUBLISHED
        yield make_post(**kwargs)


def make_user(**kwargs):
    return User(**kwargs)


def make_post(**kwargs):
    return Post(**kwargs)


def backup_flush(filename='production.json', backup=True):
    try:
        if backup:
            call_command('dumpdata', indent=2, output=filename)
            print("Dumped production database.")
        call_command('flush', no_input=True, skip_checks=True)

    except Exception as e:
        print(str(e))



def is_future(date):
    today = datetime.datetime.now()
    delta = today - date
    return delta.total_seconds() < 0


def build_fixture(
    *,
    user_count=20,
    password='onefullsend',
    post_count=50,
    since='-2y',
    future=False,
    **kwargs
):
    backup_flush()
    for user in user_gen(count=user_count, password=password):
        user.save()
        print(f"Test User: {user.username}")

    for post in post_gen(count=post_count, since=since, future=future):
        print("Generated post by {post.author.username} >>> \n{post.title}\n\n")
        post.save()

    backup_flush(filename='./blog/fixtures/test_data.json')
    print("Done")
