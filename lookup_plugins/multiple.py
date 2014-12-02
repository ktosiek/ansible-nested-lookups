import collections

from ansible.utils.plugins import lookup_loader
from ansible.utils.template import template


class LookupModule(object):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):
        print 'TERMS:', terms
        print 'inject.keys():', inject.keys()
        print 'kwargs:', kwargs
        items = [None]
        for command in terms:
            if isinstance(command, (list, basestring)):
                # Simple value - use _command_apply to template it
                items = self._command_apply('apply', '{{item}}', [command], inject)
                items = next(items)
            elif isinstance(command, dict):
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
            else:
                raise ValueError('Unknown lookup command: {}'.format(command))
            items = list(items)
            print items

        return list(items)

    def _command_apply(self, command, arg, items, inject):
        """Create new value for each item by templating it"""
        for item in items:
            if '{{' not in arg:
                arg = '{{%s}}' % arg
            yield template(self.basedir, arg, dict(inject, item=item))
