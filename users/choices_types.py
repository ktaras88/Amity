class ProfileRoles:
    AMITY_ADMINISTRATOR = 1
    SUPERVISOR = 2
    COORDINATOR = 3
    OBSERVER = 4
    RESIDENT = 5

    CHOICES = (
        (AMITY_ADMINISTRATOR, 'amity_administrator'),
        (SUPERVISOR, 'supervisor'),
        (COORDINATOR, 'coordinator'),
        (OBSERVER, 'observer'),
        (RESIDENT, 'resident'),
    )
