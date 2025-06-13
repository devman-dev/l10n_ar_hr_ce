{
    "name": "Payroll Features Educational Tuc",
    "version": "1.0.0",
    "summary": "Extensión de nómina para el sector educativo de Tucumán",
    "author": "Devman",
    "website": "https://www.devman.com.ar",
    "maintainer": "Matias Banega - DEVMAN",
    "license": "LGPL-3",
    "category": "Payroll",
    "depends": ["payroll_features", "payroll"],
    "description": """
        Módulo de extensión para payroll_features que agrega funcionalidades
        específicas para el cálculo de haberes en el sector educativo de Tucumán.
        
        Características principales:
        * Campos adicionales para puntos e índices en estructuras salariales
        * Integración con sistema de puntajes docentes
    """,
    "data": [
        "views/hr_payroll_structure_views.xml",
        "views/res_company_views.xml",
        "views/hr_employee_view.xml",
        "views/hr_contract_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "sequence": 1,
}
