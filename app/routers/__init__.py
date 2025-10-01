#from . import afps, bosses, locations, positions, register_company, workers
from .auth import register, verify_email ,login, refresh
from . import epp, odi
from . import register_company
from . import workers

routers = [
    #afps.router,
    #bosses.router,
    #locations.router,
    #positions.router,
    #register_company.router,
    #workers.router,
    #login.router,
    register.router,
    verify_email.router,
    refresh.router,
    login.router,
    epp.router,
<<<<<<< HEAD
    odi.router,
    register_company.router
=======
    register_company.router,
    workers.router
>>>>>>> dec1cbf01388fcecf82bf4ddcbfde2074526fd23
]
