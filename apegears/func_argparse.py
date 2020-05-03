"""
``ApeGeargs`` <-> ``func_argparse`` integration.

This module customizes the ``func_argparse``
argparser-generator to generate an ``ApeGeargs`` argparser.

To activate, simply import ``apegears.func_argparse`` instead of ``func_argparse``.
"""

import collections

import func_argparse
from func_argparse import (
    ArgparserGenerator as _ArgparserGenerator,
    ArgumentSpec as _ArgumentSpec,
    _is_option_type, _GenericAlias)

from .parser import ArgumentParser


################################################################################
# Definition of the our custom ArgumentParser generator

class ApegearsArgumentSpec(_ArgumentSpec):

    def __init__(self, adder_name, *flags, **kwargs):
        self.adder_name = adder_name
        super().__init__(*flags, **kwargs)

    def add_to_parser(self, parser):
        adder = getattr(parser, self.adder_name)
        adder(*self.flags, **self.kwargs)


class ApegearsGenerator(_ArgparserGenerator):

    ArgParser = ArgumentParser

    def _gen_param_arguments(self, arg_name, arg_type, doc, default, has_default, prefix):

        a = arg_name
        t = arg_type

        flags = [a]
        if prefix is not None and prefix != a:
            flags = [prefix] + flags

        kwargs = dict(
            help=doc,
        )

        if t is bool:
            adder = 'add_flag'

        else:

            required = not has_default
            if required and _is_option_type(t):
                t = t.__args__[0]
                required = False
                if not has_default:
                    default = None
                    has_default = True

            kwargs['required'] = required
            if has_default:
                kwargs['default'] = default

            adder = 'add_optional'

            # try list option
            elem_t = _get_list_contained_type(t)
            if elem_t is not None:
                adder = 'add_list'
                kwargs.update(type=_get_type(elem_t), required=False)

            else:
                # try dict option
                ktvt = _get_dict_contained_types(t)
                if ktvt is not None:
                    adder = 'add_dict'
                    kt, vt = ktvt
                    kwargs.update(key_type=_get_type(kt), type=_get_type(vt), required=False)

                else:
                    kwargs['type'] = _get_type(t)

        yield ApegearsArgumentSpec(adder, *flags, **kwargs)


def _get_type(t):
    # all supported types are already directly supported by our ArgumentParser
    return t


def _get_list_contained_type(t):
    if not isinstance(t, _GenericAlias):
        return None
    if t.__origin__ not in (list, collections.abc.Sequence):
        return None
    contained = t.__args__[0]
    assert isinstance(contained, type)
    return contained


def _get_dict_contained_types(t):
    if not isinstance(t, _GenericAlias):
        return None
    if t.__origin__ not in (dict, collections.abc.Mapping):
        return None
    kt, vt = t.__args__
    assert isinstance(kt, type)
    assert isinstance(vt, type)
    return kt, vt


################################################################################
# bootstrapping

# activate our custom generator:
func_argparse.set_default_generator(ApegearsGenerator)

# make any name importable from here, so users can change any line like
# `from func_argparse import ...`
# to
# `from apegears.func_argparse import ...`
from func_argparse import *


################################################################################
