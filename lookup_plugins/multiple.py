import collections
from itertools import chain

from ansible.utils.plugins import lookup_loader
from ansible.utils import safe_eval
from ansible.utils.template import template


class LookupModule(object):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):
        if inject is None:
            inject = {}
        items = [None]
        for command in terms:
            if isinstance(command, (list, basestring)):
                # Simple value - use _command_items to template it
                items = self._command_items('items', command, [], inject)
            elif isinstance(command, dict):
                register_name = command.pop('register', None)

                assert len(command) == 1
                command_name = command.keys()[0]
                command_arg = command.values()[0]
                if command_name.startswith('with_'):
                    command_fun = self._command_lookup
                    command_name = command_name[len('with_'):]
                else:
                    command_fun = getattr(self, '_command_' + command_name)

                items = command_fun(command_name,
                                    command_arg,
                                    items, inject)

                if register_name is not None:
                    inject[register_name] = items
            else:
                raise ValueError('Unknown lookup command: {}'.format(command))

        return list(items)

    def _command_apply(self, command, arg, items, inject):
        """Create new value for each item by templating it"""
        for item in items:
            if '{{' not in arg:
                arg = '{{%s}}' % arg
            yield template(self.basedir, arg, dict(inject, item=item))

    def _command_filter(self, command, arg, items, inject):
        """Return only the items for which filter is true"""
        if '{{' not in arg:
            arg = '{{%s}}' % arg
        for item in items:
            template_vars = dict(inject, item=item)
            decision = safe_eval(
                template(self.basedir, arg, template_vars),
                locals=template_vars)
            if decision:
                yield item

    def _command_items(self, command, arg, items, inject):
        """Create new value of items by templating the arg"""
        items = template(self.basedir, arg, inject)
        assert isinstance(items, collections.Iterable)
        return items

    def _command_lookup(self, lookup_name, arg, items, inject):
        """Apply a lookup plugin to items"""
        lookup = lookup_loader.get(lookup_name, basedir=self.basedir)
        if lookup is None:
            raise ValueError('Unknown lookup plugin: {}'.format(lookup_name))
        context = dict(inject, items=list(items))
        return lookup.run(arg, context)
