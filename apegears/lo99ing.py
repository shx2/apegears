"""
``ApeGeargs`` <-> ``lo99ing`` integration.

If lo99ing is installed, a -L/--log-levels option is automatically added to parsers,
to allow setting log-level overrides from cli.
"""

try:
    import lo99ing
except ImportError as e:
    lo99ing = None
    _import_error = e


################################################################################

def add_log_levels_option(parser, *args, force=False, **kwargs):
    if lo99ing is None:
        if force:
            raise _import_error
        return None

    return parser.add_dict(
        *args,
        type='log_level',
        key_metavar='LOGGER',
        post_process=_post_process_log_levels,
        **kwargs
    )


def _post_process_log_levels(cli_levels):
    logger = lo99ing.get_logger('lo99ing')
    for logger_name, level in cli_levels.items():
        logger.info('LOG LEVEL OVERRIDE: %s = %s', logger_name, level)
        lo99ing.set_log_level_override(logger_name, level)
    return cli_levels


################################################################################
