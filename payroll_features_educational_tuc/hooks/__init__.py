from .contract_patch import remove_contract_check_method

def apply_monkey_patch(cr, registry):
    """
    Hook post_init para aplicar el monkey patch una vez que Odoo cargó el entorno completo.
    """
    from odoo.api import Environment
    env = Environment(cr, SUPERUSER_ID, {})
    remove_contract_check_method(env)