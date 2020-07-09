from django.contrib.auth.tokens import PasswordResetTokenGenerator


class JobConfirmTokenGenerator(PasswordResetTokenGenerator):
    # TODO: email_confirmed replace
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.email_confirmed)
        )

job_confirm_token = JobConfirmTokenGenerator()
