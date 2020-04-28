"""
TBD
"""

# TBD: help per argument (also -- should include type)

import inspect
import typing

from .parser import ArgumentParser


################################################################################

def cli_func_call(
        func, args=None, description=None, arg_overrides=None,
        parser_kwargs=None, **namespace):
    """
    TBD
    """

    # create the parser:
    if description is None:
        description = func.__doc__
    if parser_kwargs is None:
        parser_kwargs = {}
    argparser = ArgumentParser(description=description, **parser_kwargs)

    # add parser arguments to reflect the function
    signature = inspect.Signature.from_callable(func)
    if arg_overrides is None:
        arg_overrides = {}
    argparser_from_signature(
        signature,
        argparser=argparser,
        arg_overrides=arg_overrides,
        **namespace
    )

    # parse cli:
    parsed_args = argparser.parse_args(args=args)

    # call the function:
    # TBD: probably not working if VAR_POSITIONAL
    positionals = [
        getattr(parsed_args, k)
        for k in argparser.positional_dests()
    ]
    optionals = {
        k: getattr(parsed_args, k)
        for k in argparser.optional_dests()
        if hasattr(parsed_args, k)
    }
    return func(*positionals, **optionals)


def argparser_from_signature(
        signature,
        argparser=None, parser_kwargs=None,
        arg_overrides=None,
        **namespace):
    """
    TBD
    """
    # TBD: allow overrides
    if isinstance(signature, str):
        signature = function_signature_from_string(signature, **namespace)
    if argparser is None:
        if parser_kwargs is None:
            parser_kwargs = {}
        argparser = ArgumentParser(**parser_kwargs)

    if arg_overrides is None:
        arg_overrides = {}

    for pname, param in signature.parameters.items():
        ov = arg_overrides.get(pname, {})
        _add_param_to_argparse(argparser, param, **ov)

    return argparser


def _add_param_to_argparse(ap, p, **overrides):

    # TBD: type=user-defined classes

    pname = p.name
    has_default = p.default != p.empty

    kwargs = dict(overrides)

    def add_if_not_empty(attr, k):
        v = getattr(p, attr)
        if v != p.empty:
            kwargs.setdefault(k, v)

    add_if_not_empty('default', 'default')

    if p.kind == p.POSITIONAL_OR_KEYWORD:
        # this is the "simple" param kind
        # we treat positional-or-keyword as positional
        is_positional = True
        add_func = ap.add_positional

    elif p.kind == p.VAR_POSITIONAL:
        # this is the "*args" part
        # positional with 0 or more => nargs='*'
        is_positional = True
        add_func = ap.add_positional
        kwargs.setdefault('nargs', '*')

    elif p.kind == p.KEYWORD_ONLY:
        # this is a param which comes after the '*' marker
        # keyword only => optional
        is_positional = False

        if p.annotation is bool:
            # a bool optional is a flag
            add_func = ap.add_flag
            kwargs.pop('type', None)
            explicit_default = kwargs.pop('default', None)
            if explicit_default:
                raise ValueError(
                    '%s: a flag with default=%r is not supported' % (pname, explicit_default))

        else:
            add_func = ap.add_optional
            if not has_default:
                kwargs.setdefault('required', True)

    elif p.kind == p.VAR_KEYWORD:
        # this is the "**kwargs" part
        is_positional = False
        raise NotImplementedError('VAR_KEYWORD is not supported')

    else:
        raise NotImplementedError(p.kind)  # presumably POSITIONAL_ONLY

    # type
    ant = p.annotation
    resolved_type = False
    if isinstance(ant, type):

        # list
        if issubclass(ant, (list, tuple)):
            if is_positional:
                kwargs.setdefault('nargs', '*')
            else:
                add_func = ap.add_list
            try:
                t, = ant.__args__
            except (AttributeError, TypeError):
                pass
            else:
                t = _resolve_annotation_type(t)
                if t is not None:
                    kwargs.setdefault('type', t)
            resolved_type = True

        # dict
        elif issubclass(ant, dict):
            if is_positional:
                raise NotImplementedError('positional dict arguments are not supported')
            add_func = ap.add_dict
            try:
                kt, vt = ant.__args__
            except (AttributeError, TypeError):
                pass
            else:
                kt = _resolve_annotation_type(kt)
                vt = _resolve_annotation_type(vt)
                if kt is not None:
                    kwargs.setdefault('key_type', kt)
                if vt is not None:
                    kwargs.setdefault('type', vt)
            resolved_type = True

    if not resolved_type:
        t = _resolve_annotation_type(ant)
        if t is not None:
            kwargs.setdefault('type', t)

    # if not is_positional:
    #    kwargs.setdefault('dest', pname)

    print(add_func.__name__, pname, kwargs)  # TBD

    add_func(pname, **kwargs)
    return ap


def _resolve_annotation_type(t):
    if t == inspect._empty:
        return None
    if not isinstance(t, type):
        return t
    if t in [typing.Any, typing.AnyStr]:
        return None
    return t


def function_signature_from_string(signature_string, **global_vars):
    """
    TBD

    Taken from https://stackoverflow.com/a/61216199/2096752
    """
    local_vars = dict()

    # support standard typing types
    global_vars = dict(
        [
            (attr, getattr(typing, attr))
            for attr in typing.__all__
        ],
        **global_vars
    )

    exec(
        '''
import inspect
def __func(%s): pass
signature = inspect.signature(__func)
        ''' % signature_string,
        global_vars,
        local_vars,
    )
    return local_vars['signature']


################################################################################
