from django.utils.translation import ugettext as _

NEW_ENTREPRENEUR_ADMIN = 10
NEW_JOB_OFFER = 20
NEW_APPLICANTS = 30
NEW_MESSAGE_TO_COMPANY = 40
NEW_COMPANY_SCORE = 50
UPDATED_TERMS = 60
UPDATED_PRIVACY_POLICY = 70
OLD_JOB_OFFER_CLOSED = 80
DEACTIVATED_COMPANY = 90
DELETED_COMPANY = 100
TRANSFERED_COMPANY = 110
DELETED_MEMBERSHIP = 120

NOTIFICATION_TYPE_CHOICES = (
    (NEW_ENTREPRENEUR_ADMIN, _('Invitation to administer company.')),
    (NEW_JOB_OFFER, _('New job offer that may interest you.')),
    (NEW_APPLICANTS, _('New applicants to my job offer.')),
    (NEW_MESSAGE_TO_COMPANY, _('New message to company.')),
    (NEW_COMPANY_SCORE, _('New company score.')),
    (UPDATED_TERMS, _('New user agreement.')),
    (UPDATED_PRIVACY_POLICY, _('New company score.')),
    (OLD_JOB_OFFER_CLOSED, _('Old job offer has been closed.')),
    (DEACTIVATED_COMPANY, _('Company has been deactivated.')),
    (DELETED_COMPANY, _('Company has been deleted.')),
    (TRANSFERED_COMPANY, _('Company has been transfered.')),
    (DELETED_MEMBERSHIP, _('Administrator membership has been deleted.')),
)
