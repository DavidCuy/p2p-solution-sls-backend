# -*- coding: utf-8 -*-
from unittest import TestCase

import peewee
from db_b2c.base_model import BaseModel
from core_utils.utils import (
    compare_iterables,
)
from peewee import (
    BigAutoField,
    TextField,
)

from .models_validator import Validator


class TestModel(BaseModel):
    id = BigAutoField()
    name = TextField(null=True)

    class Meta:
        table_name = "Test"
        schema = "Test"


class Test(TestCase):
    def setUp(self):
        self.validator = Validator(verbose=True)

    def test_get_all_models(self):
        all_models = self.validator.get_all_models()
        self.assertIsInstance(all_models, list)
        self.assertIsInstance(all_models[0][1], str)
        self.assertTrue(issubclass(all_models[0][0], peewee.Model))

    def test_validate_models(self):
        result = self.validator.validate_models(self.validator.get_all_models())
        self.assertIsInstance(result, dict)
        self.assertTrue(compare_iterables(["ok", "error"], result))

    def test_review_results(self):
        self.validator.review_results(
            self.validator.validate_models(self.validator.get_all_models())
        )

    def test_review_results_error(self):
        all_models = self.validator.get_all_models()
        all_models.append((TestModel, "testModel"))
        with self.assertRaises(ValueError):
            self.validator.review_results(self.validator.validate_models(all_models))

    def test_process(self):
        self.validator.process()
