import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SP = os.environ.get('GK_SCRATCH', '/private/tmp/claude-501/-Users-sipiyou-Documents-elsasko/1f21b929-2b2f-4c47-994f-366d5097ed47/scratchpad/greek')
os.makedirs(SP, exist_ok=True)
