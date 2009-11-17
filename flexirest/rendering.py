import itertools
import os
import sys

from docutils import writers
from docutils.parsers.rst import roles
from docutils.core import publish_parts

from flexirest import tex

__docformat__ = 'reStructuredText'

pseudo_writers = {'latex2pdf': 'latex'}

"""
An iterator of all legal writer names.

XXX Beware: the _writer_aliases dict is undocumented and marked as
private! In theory we should find out a better way to produce this
list, but right now I don't see any way of doing that.
"""
all_writers = lambda: sorted(set(itertools.chain(writers._writer_aliases.keys(),
                              writers._writer_aliases.values(), pseudo_writers)))

def _register_roles(conf):
    """
    Registers roles to be used in this run.

    `conf` - configuration module.
    """

    for rolecand, rolename in ((getattr(conf, role), role) for role in
                   dir(conf) if role.startswith('role_')):
        if callable(rolecand):
            roles.register_canonical_role(rolename[5:], rolecand)

class Render(object):
    """
    The `Render` object is a (somewhat) stateful representation of the
    rendering process. It's main purpose is to run the rendering
    stepwise, therefore enabling the two-step writing mechanism.
    """

    def __init__(self, conf, options, template, writer_name):
        self.conf = conf
        self.options = options
        self.template = template
        self.writer = writer_name

    def _build_settings(self):
        _register_roles(self.conf)
        return getattr(self, '_build_%s_settings' % self.docutils_writer, lambda: {})()

    def dump_parts(self, source, destination):
        """
        Writes a mini-report on what parts where created by the specified
        `docutils` writer (intended for human consumption).

        `parts` - parts `dict` created by `docutils.core.publish_parts()`
        `out` - output stream to write to.
        """

        title = "Parts created by the docutils writer '%s'" % self.writer
        destination.write(title + os.linesep)
        destination.write(len(title) * '-')
        destination.write(2 * os.linesep)
        destination.write('Part keys: ' + 2 * os.linesep)

        parts = self.publish_parts(source)
        destination.write(os.linesep.join(sorted(parts.keys())))
        destination.write(2 * os.linesep)
        for part in parts:
            destination.write("Value of part '%s':%s" % (part, os.linesep))
            destination.write(parts[part] + os.linesep)
            destination.write(80*'-'+os.linesep)
            destination.write(os.linesep)

    @property
    def docutils_writer(self):
        """
        The actual `docutils` writer. In the case of pseudo writers
        this will be different from the writer name specified to the
        frontend (for example, the `latex2pdf` writers
        `docutils_writer` will be 'latex'.
        """
        if self.writer in pseudo_writers:
            return pseudo_writers[self.writer]
        return self.writer

    def publish_parts(self, source):
        # The .read().decode(..) chain below is a little inefficient, but
        # this is supposed to be a quite modest tool, so I'll just leave
        # it be for now..
        parts = publish_parts(
            source=source.read().decode('utf8'),
            writer_name=self.docutils_writer,
            settings_overrides=self._build_settings(),
        )
        parts['lang'] = self.options.lang
        return parts

    def default_writer(self, stage_one, destination):
        """
        The default writer just writes out the template applied output
        from publich_parts().
        """
        destination.write( stage_one.encode("utf-8") )

    def render(self, source, destination):
        parts = self.publish_parts(source)
        getattr(self, '_write_%s' % self.writer,
                self.default_writer)(self.template % parts, destination)
        destination.flush()

    def _build_html_settings(self):
        return {}

    def _build_latex_settings(self):
        return {'output_encoding': 'utf-8', # XXX should probably support more..
                'language_code': self.options.lang}

    _build_latex2e_settings = _build_latex_settings
    _build_latex2pdf_settings = _build_latex_settings

    def _write_latex2pdf(self, latex, destination):
        """
        Uses the `flexirest.tex` module to render PDF.
        """
        pdf = tex.latex2pdf(latex)
        destination.write(pdf)

def render(source, destination, conf, options, template, writer_name):

    """API entry point (helper for the most obvious case).

    A call expected to succed must provide all parameters. See
    flexirest.main.commandline() to find sensible defaults.

    `source` - file-like object to read input from.
    `destination` - file-like object (needs at least `.write()` and `.flush()`
                  methods.
    `conf` - configuration module.
    `options` - commandline options
    `template` - the template to enter the results of `publish_parts()` into.
               (needs to support formatting with the '..' % {} technique.)
    `writer_name` - name of the `docutils` writer to use.
    """

    renderer = Render(conf, options, template, writer_name)
    renderer.render(source, destination)

def dump_parts(source, destination, conf, options, template, writer_name):

    """API entry point for the `dump_parts` option.

    A call expected to succed must provide all parameters. See
    flexirest.main.commandline() to find sensible defaults.

    `source` - file-like object to read input from.
    `destination` - file-like object (needs at least `.write()` and `.flush()`
                  methods.
    `conf` - configuration module.
    `options` - commandline options
    `template` - the template to enter the results of `publish_parts()` into.
               (needs to support formatting with the '..' % {} technique.)
    `writer_name` - name of the `docutils` writer to use.
    """

    renderer = Render(conf, options, template, writer_name)
    renderer.dump_parts(source, destination)
