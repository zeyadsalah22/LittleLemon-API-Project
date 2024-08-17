from rest_framework.throttling import UserRateThrottle

class ManagerRateThrottle(UserRateThrottle):
    scope = 'manager'

class DeliveryRateThrottle(UserRateThrottle):
    scope = 'delivery'

class CustomerRateThrottle(UserRateThrottle):
    scope = 'customer'