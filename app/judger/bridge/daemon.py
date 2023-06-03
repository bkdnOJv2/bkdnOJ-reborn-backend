import logging
import signal
import threading
from functools import partial

from django.conf import settings

from judger.bridge.django_handler import DjangoHandler
from judger.bridge.judge_handler import JudgeHandler
from judger.bridge.judge_list import JudgeList
from judger.bridge.server import Server
from judger.models import Judge
from submission.models import Submission

logger = logging.getLogger('judge.bridge')


def reset_judges():
    Judge.objects.update(online=False, ping=None, load=None)


def judge_daemon():
    reset_judges()
    Submission.objects.filter(status__in=Submission.IN_PROGRESS_GRADING_STATUS) \
        .update(status='IE', result='IE', error=None)
    judges = JudgeList()

    judge_server = Server(settings.BRIDGED_JUDGE_ADDRESS, partial(JudgeHandler, judges=judges))
    django_server = Server(settings.BRIDGED_DJANGO_ADDRESS, partial(DjangoHandler, judges=judges))

    threading.Thread(target=django_server.serve_forever).start()
    threading.Thread(target=judge_server.serve_forever).start()

    stop = threading.Event()

    def signal_handler(signum, _):
        logger.info('Exiting due to %s', signal.Signals(signum).name)
        stop.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        stop.wait()
    finally:
        django_server.shutdown()
        judge_server.shutdown()
