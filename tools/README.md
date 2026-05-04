# tools/

Repo-hygiene scripts. stdlib only.

- `chat_paste_check.py`   detect chat-paste contamination
- `chat_paste_fix.py`     auto-fix the mechanical subset

Run on staged files before commit:

    python tools/chat_paste_check.py --staged

Run on the whole tree:

    find . -name "*.py" -not -path "./.git/*" -print0 \
      | xargs -0 python tools/chat_paste_check.py

Auto-fix the mechanical subset (smart quotes, ellipsis,
bold-dunders, lone ``` fences):

    python tools/chat_paste_fix.py path/to/file.py
