import django


from django.db import transaction
from django.test import TestCase

from .models import Organization, Project, Repository, RepositoryView, DataSource

# Create your tests here.


class OrganizationModelTests(TestCase):

    def test_init(self):
        # The CharField name is filled as en empty string by default, not None
        org = Organization()
        self.assertIsNot(org, None)
        org.save()

        org = Organization(name=None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                org.save()

        # Strange that in a CharField you can store dicts!
        org = Organization(name={'kk': 9000000000000000000000000000})
        org.save()


class ProjectModelTests(TestCase):

    def test_init(self):
        project = Project()
        self.assertIsNot(project, None)
        project.save()


class RepositoryModelTest(TestCase):

    def test_init(self):
        rep = Repository()
        self.assertIsNot(rep, None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                rep.save()
        ds = DataSource(name='git')
        ds.save()
        rep = Repository(data_source=ds)
        rep.save()


class RepositoryViewModelTests(TestCase):

    def test_init(self):
        rview = RepositoryView()
        self.assertIsNot(rview, None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                rview.save()

        ds = DataSource(name='git')
        ds.save()
        rep = Repository(data_source=ds, name='test')
        rview = RepositoryView(rep=rep)
        # rep must be saved before using it in rview above
        # it is saved before rview but it fails because of that
        rep.save()
        with self.assertRaises(django.db.utils.IntegrityError):
            with transaction.atomic():
                rview.save()

        # rep is saved already so we can now use it
        rview = RepositoryView(rep=rep)
        rview.save()

        return


class DataSourceModelTests(TestCase):

    def test_init(self):
        ds = DataSource()
        self.assertIsNot(ds, None)
        ds.save()
