from submission.models import Submission
sub = Submission.objects.get(id=18)
sub.judge(force_judge=True)