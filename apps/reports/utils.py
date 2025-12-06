from django.apps import apps as django_apps


def get_model(app_label, model_name):
    return django_apps.get_model(app_label, model_name)
