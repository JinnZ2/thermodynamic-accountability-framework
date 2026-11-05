#!/usr/bin/env python3
# misuse_guard/localdata.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# D-M1 method, not data. Committed fixtures are synthetic. Real registries
# (holders, holdings, exact trigger values, logs) live in local_data/ at the
# repo root, which is gitignored, or anywhere outside the repo tree.
#
# load_real_json(path) refuses a path that is inside the repo tree unless it
# is under local_data/ AND local_data/ is listed in the repo .gitignore. It
# reads nothing it refuses. This protects against committing real data by
# accident; it does not protect the device that holds it.

import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DIR = os.path.join(REPO_ROOT, "local_data")


class RealDataRefused(ValueError):
    pass


def _inside(child, parent):
    child, parent = os.path.realpath(child), os.path.realpath(parent)
    return child == parent or child.startswith(parent + os.sep)


def local_dir_ignored(repo_root=REPO_ROOT):
    try:
        with open(os.path.join(repo_root, ".gitignore"), encoding="utf-8") as f:
            lines = [l.strip() for l in f]
    except OSError:
        return False
    return any(l in ("local_data/", "/local_data/", "local_data", "/local_data") for l in lines)


def check_real_path(path, repo_root=REPO_ROOT):
    """Return the resolved path, or raise RealDataRefused."""
    p = os.path.realpath(path)
    if not _inside(p, repo_root):
        return p
    local = os.path.join(repo_root, "local_data")
    if not _inside(p, local):
        raise RealDataRefused("real data inside the repo tree is refused: %s (put it in local_data/, "
                              "which is gitignored, or outside the repo)" % os.path.relpath(p, repo_root))
    if not local_dir_ignored(repo_root):
        raise RealDataRefused("local_data/ is not listed in .gitignore; refusing to read real data from it")
    return p


def load_real_json(path, repo_root=REPO_ROOT):
    with open(check_real_path(path, repo_root), encoding="utf-8") as f:
        return json.load(f)
