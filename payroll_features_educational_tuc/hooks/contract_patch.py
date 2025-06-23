import logging

_logger = logging.getLogger(__name__)

def remove_contract_check_method(env):
    """
    Elimina el método _check_contracts del modelo hr.contract si existe.
    Debe llamarse desde una función post-init o desde ready().
    """
    Contract = env['hr.contract'].__class__
    if hasattr(Contract, '_check_contracts'):
        delattr(Contract, '_check_contracts')
        _logger.warning("✅ Monkey patch aplicado: _check_contracts eliminado de hr.contract")

