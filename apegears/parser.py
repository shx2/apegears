"""
Definition of the ApeGears ArgumentParser class.
"""

import argparse as _ap
from collections import OrderedDict

try:
    import argcomplete
except ImportError:
    argcomplete = None  # argcomplete not installed

from .misc import _ExtendAction, _SetItemAction, _KeyValueType, _StrictDefaultActionWrapper
from .spec import find_spec as _find_spec


################################################################################
# Our ArgumentParser class

class ArgumentParser(_ap.ArgumentParser):
    """
    This class is fully compatible with the standard argparse.ArgumentParser, and provides
    some features:

    - Adder methods: add_positional, add_optional, add_flag, add_list.
    - Dict arguments
    - Custom argument-types using "specs"
    - Support for some standard python types
    - Support for enum arguments
    - Workaround append-with-nonempty-default bug

    """

    _REQUIRED_IS_NONEMPTY_ACTIONS = (_ExtendAction, _SetItemAction)

    ################################################################################

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # register our actions
        self.register('action', 'extend', _ExtendAction)
        self.register('action', 'setitem', _SetItemAction)

    ################################################################################
    # parse_args()

    def parse_known_args(self, *args, **kwargs):
        # invoke pre-parse hook:
        self._pre_parse(*args, **kwargs)

        # call super:
        namespace, extras = super().parse_known_args(*args, **kwargs)

        # run arg post processors:
        self._run_post_processors(namespace)

        # enforce required args:
        self._enforce_required(namespace)

        # invoke post-parse hook:
        self._post_parse(namespace, extras)

        return namespace, extras

    def _pre_parse(self, *args, **kwargs):
        self._pre_parse_argcomplete(*args, **kwargs)

    def _post_parse(self, namespace, extras):
        pass

    ################################################################################
    # add_argument()

    def add_argument(self, *args,
                     strict_default=False, post_process=None, completer=None,
                     **kwargs):
        """
        :param strict_default: whether to enable workaround issue16399
        :param post_process: a callable to apply to the argument post-parsing, in place
        :param completer: a custom argcomplete completer
        """

        # workaround append-with-nonempty-default issue (https://bugs.python.org/issue16399):
        if strict_default:
            action = self._get_strict_default_action(kwargs.get('action'))
            if action is not None:
                kwargs['action'] = action

        # metavar defaulting
        metavar = kwargs.get('metavar')
        type = kwargs.get('type')
        if metavar is None and type is not None:
            type_metavar = getattr(type, '__metavar__', None)
            if type_metavar is not None:
                kwargs['metavar'] = type_metavar

        # call super:
        action = super().add_argument(*args, **kwargs)

        # remember post processor for later
        if post_process is not None:
            action.post_process = post_process

        # argcomplete
        self._set_completer(action, completer)

        return action

    ################################################################################
    # add_xxx() convenience methods

    def add_positional(self, name=None, **kwargs):
        """
        Add a positional argument to the parser.  This calls ``add_argument`` with appropriate
        values.

        :param kwargs:
            Supports all kwargs supported by ``add_argument``, except for action and required.
        """

        names = [name] if name else []
        names, kwargs = self._use_spec(*names, is_positional=True, **kwargs)

        if names and names[0] and names[0][0] in self.prefix_chars:
            raise ValueError('name of positional must not start with %r' % self.prefix_chars)
        for k in ['action', 'required']:
            if k in kwargs:
                raise ValueError('%s= does not apply to positionals' % k)

        nargs = kwargs.pop('nargs', None)
        if 'default' in kwargs:
            # a positional with a default value
            if nargs is None:
                nargs = '?'
            if nargs != '?':
                raise ValueError(
                    'nargs=%s does not apply to a positional with a default value' % nargs)

        return self.add_argument(
            *names,
            action=None,
            nargs=nargs,
            **kwargs
        )

    def add_optional(self, *flags, **kwargs):
        """
        Add an *optional* parameter.  This calls ``add_argument`` with appropriate values.

        :param flags:
            supports flags with prefix ("-", "--") omitted. Prefix will be added automaticallly.
        :param kwargs:
            supports all kwargs supported by ``add_argument``.

        :note: "optional" is ``argparse``'s way of saying "non-positional".  An "optional" argument
            is non-positional, but is not necessarilly *optional*, i.e. you can set required=True.
        """
        flags, kwargs = self._use_spec(*flags, is_positional=False, **kwargs)
        if not flags:
            raise ValueError('name not supplied for optional')
        flags = [self._fix_flag(flag) for flag in flags]
        return self.add_argument(*flags, **kwargs)

    def add_flag(self, *flags, include_negative=True, **kwargs):
        """
        Add an *optional* boolean flag.  This calls ``add_argument`` with appropriate values.

        :param flags:
            same as ``add_optional``
        :param kwargs:
            supported kwargs: dest, help, metavar.
        :param include_negative:
            if True, will also add an hidden negative flag with prefix "--no-"
        """

        flags = [self._fix_flag(flag) for flag in flags]

        for k in ['action', 'nargs', 'required', 'const', 'default', 'type', 'choices']:
            if k in kwargs:
                raise ValueError('%s= does not apply to flags' % k)

        action = self.add_argument(*flags, action='store_true', **kwargs)

        if include_negative:
            negative_flags = self._get_negative_flags(flags)
            kwargs.pop('dest', None)
            kwargs.pop('help', None)
            self.add_argument(
                *negative_flags,
                action='store_false',
                dest=action.dest,
                help=_ap.SUPPRESS,
                **kwargs
            )

        return action

    def add_list(self, *flags, strict_default=True, **kwargs):
        """
        Add an *optional* list argument.  This calls ``add_argument`` with appropriate values.

        :param flags:
            same as ``add_optional``
        :param kwargs:
            Supports all kwargs supported by ``add_argument``, except for action.
            nargs is typically not required.
        :param strict_default: whether to enable workaround issue16399

        :note: The default default value is an empty list.
        :note: required=True means a **non-empty** list is required.
        """
        flags, kwargs = self._process_collection_optional(list, 'list', *flags, **kwargs)
        flags, kwargs = self._use_spec(*flags, is_positional=False, **kwargs)
        return self.add_argument(
            *flags,
            action='extend',
            strict_default=strict_default,
            **kwargs
        )

    def add_dict(self, *flags, key_type=None, key_metavar=None, strict_default=True, **kwargs):
        """
        Add an *optional* dict argument, where each item is of the form "KEY=VALUE".
        This calls ``add_argument`` with appropriate values.

        :param flags:
            same as ``add_optional``
        :param kwargs:
            Supports all kwargs supported by ``add_argument``, except for action and choices.
            type refer to the *VALUE part* of the KEY=VALUE pair.
            metavar refers to the KEY=VALUE pair, not just the value.
            nargs is typically not required.
        :param key_type, key_metavar:
            Same as type and metavar, but refers to the *KEY part* of the key=value pair.
        :param strict_default: whether to enable workaround issue16399

        :note: the resulting dict is an OrderedDict, reflecting cli order.
        :note: The default default value is an empty ``OrderedDict``.
        :note: required=True means a **non-empty** dict is required.
        """

        # note: choices is not supported
        if 'choices' in kwargs:
            raise ValueError('choices= is not supported for dict')

        explicit_metavar = kwargs.get('metavar')

        flags, kwargs = self._process_collection_optional(OrderedDict, 'dict', *flags, **kwargs)
        flags, kwargs = self._use_spec(*flags, is_positional=False, **kwargs)

        # note: choices is not supported. if it was set from spec, remove it
        kwargs.pop('choices', None)

        # we use our own type, which stores key_type and value_type:
        type = kwargs.pop('type', None)
        type = _KeyValueType(
            key_type, type,
            key_metavar=key_metavar, value_metavar=kwargs.get('metavar'),
        )

        # if metavar was passed explicitly, we leave it as is.
        # Else, we overwrite it (even if it was set from the spec), because the spec refers to
        # value, not key=value.
        if explicit_metavar is None:
            kwargs['metavar'] = type.get_metavar()

        return self.add_argument(
            *flags,
            type=type,
            action='setitem',
            strict_default=strict_default,
            **kwargs
        )

    ################################################################################
    # argparse spec

    def _use_spec(self, *args, is_positional=None, **kwargs):
        if is_positional is None:
            is_positional = self._is_positional(*args)
        type = kwargs.get('type', None)
        if type is not None:
            spec = self._spec_from_type(type)
            if spec is not None:
                args, kwargs = self._apply_spec(spec, *args, is_positional=is_positional, **kwargs)
        return args, kwargs

    def _apply_spec(self, spec, *args, is_positional, **kwargs):

        # default to names from spec:
        if not args:
            names = spec.names
            if names and names != spec.EMPTY:
                args = tuple(names)
                if is_positional:
                    # a positional uses the first name
                    args = args[:1]
                else:
                    # add optional prefix
                    args = tuple([self._fix_flag(arg) for arg in args])

        # handle rest of the fields:

        def _setdefault(attr):
            v = getattr(spec, attr)
            if v != spec.EMPTY:
                kwargs.setdefault(attr, v)

        for attr in ['post_process', 'choices', 'help', 'metavar', 'completer']:
            _setdefault(attr)

        if not kwargs.get('required', False):
            _setdefault('default')

        kwargs['type'] = spec.from_string

        return args, kwargs

    def _spec_from_type(self, type):
        if type is None:
            return None
        spec = _find_spec(type)
        if spec is not None:
            return spec
        return None  # no spec, do standard type handling

    ################################################################################
    # workaround append-with-nonempty-default issue (https://bugs.python.org/issue16399):

    _STRICT_DEFAULT_ACTIONS = {
        _ap._AppendAction: [],
        _ExtendAction: [],
        _SetItemAction: OrderedDict(),
    }

    def _get_strict_default_action(self, action):
        action_cls = self._registry_get('action', action, action)
        if not isinstance(action_cls, type):
            return None
        for sd_action_cls, empty_value in self._STRICT_DEFAULT_ACTIONS.items():
            if issubclass(action_cls, sd_action_cls):
                return lambda *a, **kw: \
                    _StrictDefaultActionWrapper(action_cls(*a, **kw), empty_value, *a, **kw)
        return None

    ################################################################################
    # argcomplete

    def _pre_parse_argcomplete(self, *args, **kwargs):
        if argcomplete is None:
            return
        if 'IntrospectiveArgumentParser' in type(self).__name__:
            # this is a nested call triggered by previous call to argcomplete.autocomplete().
            # avoid another call to argcomplete.autocomplete()
            return
        argcomplete.autocomplete(self)

    def _set_completer(self, action, completer):
        if action is not None and completer is not None:
            action.completer = completer

    ################################################################################
    # misc

    def positional_names(self):
        return self._argument_names(self._positionals, 'name')

    def positional_dests(self):
        return self._argument_names(self._positionals, 'dest')

    def optional_names(self):
        return self._argument_names(self._optionals, 'name')

    def optional_dests(self):
        return self._argument_names(self._optionals, 'dest')

    def _argument_names(self, arggroup, field):
        return [getattr(action, field) for action in arggroup._group_actions]

    ################################################################################
    # privates

    def _enforce_required(self, namespace):
        empty_required_actions = [
            _ap._get_action_name(action)
            for action in self._actions
            if getattr(action, 'required', False)
            and isinstance(action, self._REQUIRED_IS_NONEMPTY_ACTIONS)
            and not getattr(namespace, action.dest, None)
        ]
        if empty_required_actions:
            self.error(
                _ap._('the following arguments are required: %s') %
                ', '.join(empty_required_actions)
            )

    def _run_post_processors(self, namespace):
        for action in self._actions:
            arg_name = action.dest
            post_process = getattr(action, 'post_process', None)
            if post_process is None:
                continue
            try:
                arg_value = getattr(namespace, arg_name)
            except AttributeError:
                continue
            new_arg_value = post_process(arg_value)
            setattr(namespace, arg_name, new_arg_value)

    def _process_collection_optional(self, coll_cls, coll_cls_name, *flags, **kwargs):

        for k in ['action']:
            if k in kwargs:
                raise ValueError('%s= does not apply to %ss' % (k, coll_cls_name))

        # nargs defaults to '+' (not '*', providing the flag with no value is just bad practice)
        nargs = kwargs.pop('nargs', None)
        if nargs is None:
            nargs = '+'
        if nargs == '?':
            raise ValueError('nargs=%s does not apply to %ss' % (nargs, coll_cls_name))

        # default to an empty collection:
        default = kwargs.pop('default', None)
        if default is None:
            default = coll_cls()

        kwargs.update(
            default=default,
            nargs=nargs,
        )

        flags = [self._fix_flag(flag) for flag in flags]

        return flags, kwargs

    def _fix_flag(self, flag):
        """
        For optionals, add an appropriate prefix if needed.
        E.g. 'x' --> '-x', 'yy' --> '--yy'.
        """
        if (not flag) or flag[0] in self.prefix_chars:
            return flag
        c = self.prefix_chars[0]
        if len(flag) == 1:
            return c + flag
        else:
            return (c * 2) + flag

    def _get_negative_flags(self, flags):
        long_flags = [
            f for f in flags
            if len(f) >= 2
            and f[0] in self.prefix_chars and f[1] in self.prefix_chars
        ]
        if long_flags:
            # e.g. --foo   -->   --no-foo
            f = long_flags[0]
            prefix = f[:2]
            suffix = f[2:]
        else:
            # e.g. -f   -->   --no-f
            f = flags[0]
            assert f[0] in self.prefix_chars, flags
            prefix = f[0] * 2
            suffix = f[1:]
        return ['%sno-%s' % (prefix, suffix)]

    def _is_positional(self, *args):
        # NOTE: based on code from base class

        # if no positional args are supplied or only one is supplied and
        # it doesn't look like an option string, parse a positional
        # argument
        if not args:
            return True
        if len(args) == 1:
            a, = args
            if not a or a[0] not in self.prefix_chars:
                return True
        return False


################################################################################
