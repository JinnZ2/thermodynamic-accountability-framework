#!/usr/bin/env python3
# adapters/base.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# Model access goes through an adapter. No keys live in this repository;
# a concrete adapter reads what it needs from the environment.
#
#   ModelAdapter.complete(prompt) -> text
#   CommandAdapter   runs $SIGCAL_COMMAND with the prompt on stdin, reads
#                    stdout. The command (your own script / CLI) holds any
#                    credentials. Model id and version from $SIGCAL_MODEL_ID
#                    and $SIGCAL_MODEL_VERSION.
#   ScriptedAdapter  fixed replies for tests; never calls a model.
#   SteeringAdapter  interface only (open-weights steering, T4 optional
#                    variant). NOT implemented here.

import os
import shlex
import subprocess


class AdapterError(RuntimeError):
    pass


class ModelAdapter(object):
    def __init__(self, model_id, model_version=None):
        self.model_id = model_id
        self.model_version = model_version

    def complete(self, prompt):
        raise NotImplementedError


class CommandAdapter(ModelAdapter):
    def __init__(self, command=None, model_id=None, model_version=None, timeout=600):
        command = command or os.environ.get("SIGCAL_COMMAND")
        model_id = model_id or os.environ.get("SIGCAL_MODEL_ID")
        if not command or not model_id:
            raise AdapterError("set SIGCAL_COMMAND and SIGCAL_MODEL_ID in the environment")
        ModelAdapter.__init__(self, model_id, model_version or os.environ.get("SIGCAL_MODEL_VERSION"))
        self.argv = shlex.split(command) if isinstance(command, str) else list(command)
        self.timeout = timeout

    def complete(self, prompt):
        p = subprocess.run(self.argv, input=prompt.encode("utf-8"), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=self.timeout)
        if p.returncode != 0:
            raise AdapterError("command exit %d: %s" % (p.returncode, p.stderr.decode("utf-8", "replace")[:200]))
        return p.stdout.decode("utf-8", "replace")


class ScriptedAdapter(ModelAdapter):
    """Returns replies[i] for the i-th call, or default. For tests only."""

    def __init__(self, model_id, replies=None, default="scripted reply", model_version="test"):
        ModelAdapter.__init__(self, model_id, model_version)
        self.replies, self.default, self.calls = list(replies or []), default, []

    def complete(self, prompt):
        self.calls.append(prompt)
        return self.replies.pop(0) if self.replies else self.default


class SteeringAdapter(ModelAdapter):
    """Interface for the optional steered T4 variant. Not implemented."""

    def complete_steered(self, prompt, magnitude):
        raise NotImplementedError("steering adapters are not implemented in this repository")
