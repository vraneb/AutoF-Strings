import sublime
import sublime_plugin

settings = sublime.load_settings('AutoF-Strings.sublime-settings')


class FStringsAddNeeded(sublime_plugin.TextCommand):
    def run(self, edit):

        # Regex explanation:
        #
        # (?:              Non-capturing union to allow for fstrings at beginning (necessary?)
        #   (?<=[^frbu\\]) Ensure string is not already prepended (frbu) or escaped quote
        #   |^             Beginning anchor
        # )
        # ('|\")           Match single/double quote. NOTE: " is escaped because r"" is used instead of r''
        # .*{.+}.*         String contents: detect if f-string or not
        # (?<!\\)          Make sure closing quote; not escaped
        # \1               Closing quote matches

        spots = self.view.find_all(
            r"(?:(?<=[^frbu\\])|^)('|\").*{.+}.*(?<!\\)\1")
        if spots is None:
            spots = []

        count = 0
        for spot in spots:
            self.view.insert(edit, spot.begin() + count, 'f')
            count += 1


class FStringsRemoveExtra(sublime_plugin.TextCommand):
    def run(self, edit):

        # Regex explanation:
        # See FStringsFix for more
        #
        # f            Check all strings prepended with f
        # ('|\")
        # (?!.*{.+}.*) Check that rest of string doesn't have non-empty {}
        # (?:.*)       Match rest of string
        # (?<!\\)\1

        spots = self.view.find_all(r"f('|\")(?!.*{.+}.*)(?:.*)(?<!\\)\1")
        if spots is None:
            spots = []

        count = 0
        for spot in spots:
            r = sublime.Region(spot.begin() - count, spot.begin() - count + 1)
            self.view.erase(edit, r)
            count += 1


class FStringsFix(sublime_plugin.TextCommand):
    def run(self, edit):
        stx = self.view.syntax()
        enabled = settings.get('enabled_syntaxes')
        if stx is not None and stx.name in settings.get('enabled_syntaxes'):
            self.view.run_command('f_strings_add_needed')
            self.view.run_command('f_strings_remove_extra')


class FStringsListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):

        if settings.get('fix_on_save'):
            view.run_command('f_strings_fix')
