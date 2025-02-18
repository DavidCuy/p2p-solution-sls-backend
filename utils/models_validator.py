#!/usr/bin/python3
# -*- coding: utf-8 -*-

import inspect

import core_db.base_model
import core_db.models
import peewee


class Validator:
    def __init__(self, *, verbose=True, exclude_model=None):
        self.exclude_model = ["BaseModel"] if exclude_model is None else exclude_model
        self.fmt = "{:^26}" * 4
        self.f = self.fmt.format("model", "ok", "fail", "message")
        self.verbose = verbose

    def _print(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def get_all_models(self):
        return [
            (obj, _name)
            for _name, obj in inspect.getmembers(core_db.models)
            if inspect.isclass(obj) and issubclass(obj, peewee.Model)
        ]

    def validate_models(self, all_models):
        result = {"error": [], "ok": []}
        for model, name in all_models:
            if name in self.exclude_model:
                continue
            try:
                model.select().dicts().first()
            except Exception as details:
                self._print(self.fmt.format(name, 0, 1, f"{details}"))
                self._print("-" * len(self.f))
                core_db.base_model.database.rollback()
                result["error"].append(name)
            else:
                self._print(self.fmt.format(name, 1, 0, "ok"))
                self._print("-" * len(self.f))
                result["ok"].append(name)
        return result

    def review_results(self, results):
        errors = results["error"]
        self._print(self.fmt.format("total", len(results["ok"]), len(errors), ""))
        if errors:
            self._print("{:/^104}".format("Error"))
            self._print("//{:-^100}//".format("-"))
            for e in errors:
                self._print("//{:^100}//".format(e))
                self._print("//{:-^100}//".format("-"))
            self._print("{:/^104}".format("/"))
            raise ValueError("Table not is compatible with the model")
        text = "//{:^100}//".format("Successfully finished")
        box = "/" * len(text)
        self._print(box)
        self._print(text)
        self._print(box)

    def __str__(self):
        self.process()

    def process(self):
        self._print(self.f)
        self._print("=" * len(self.f))
        _models = self.get_all_models()
        res = self.validate_models(_models)
        self.review_results(res)


if __name__ == "__main__":
    validator = Validator(verbose=True)
    validator.process()
