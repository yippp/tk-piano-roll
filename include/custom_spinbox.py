from Tkinter import *
from src.helper import dummy, isint


class _ValueList():

    def __init__(self, values, match_case=True):
        self._values = values
        self._match_case = match_case

    def __nonzero__(self):
        return not not self._values

    def __contains__(self, value):
        if not self._match_case:
            lower = [v.lower() for v in self._values]
            return value.lower() in lower
        else:
            return value in self._values

    def __iter__(self):
        for value in self._values:
            yield value

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values

    @property
    def match_case(self):
        return self._match_case

    @match_case.setter
    def match_case(self, match_case):
        self._match_case = match_case


class CustomSpinbox(Spinbox):

    def __init__(self, parent, **kwargs):
        start = kwargs.pop('start', None)
        convert = kwargs.pop('convert', None)
        match_case = kwargs.pop('match_case', None)
        callback = kwargs.pop('callback', None)

        Spinbox.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_data(start=start, convert=convert,
            match_case=match_case, callback=callback)
        self._bind_event_handlers()

    def _init_data(self, **kwargs):
        start = kwargs['start']
        convert = kwargs['convert']
        match_case = kwargs['match_case']
        callback = kwargs['callback']

        values = self.config()['values'][4].split()
        if values:
            self._values = _ValueList(values, match_case)
            self._curr_value = start if start else values[0]
        else:
            self._values = None
            from_ = str(int(self.config()['from'][4]))
            self._curr_value = start if start else from_

        self._prev_value = self._curr_value
        self._var = StringVar(self)
        self.set(self._curr_value)
        self._var.trace('w', self._update)

        self._convert = convert
        self._match_case = match_case
        self._callback = callback
        self.config(
            command=self._callback,
            textvariable=self._var,
            state='readonly')

    def _update(self, *args):
        self._curr_value = self._var.get()

    def _bind_event_handlers(self):
        self.bind('<Return>', self._on_return)
        self.bind('<KP_Enter>', self._on_return)
        self.bind('<FocusOut>', self._on_lost_focus)
        self.bind('<Key>', self._after_keypress)

    def _on_return(self, event):
        state = self.config()['state'][4]
        if state == 'readonly':
            self.config(state='normal')
        else:
            self.icursor(END)
            value = self.validate()
            self._curr_value = value
            self._prev_value = self._curr_value
            self._var.set(self._curr_value)
            self._callback()
            self.config(state='readonly')

    def _on_lost_focus(self, event):
        state = self.config()['state'][4]
        if state == 'normal':
            self.config(state='readonly')
            self.selection_clear()

            value = self.validate()
            self._curr_value = value
            self._var.set(self._curr_value)
            self._callback()

    def _after_keypress(self, event):
        self.after_idle(self.icursor, END)

    @property
    def from_(self):
        return self.config()['from'][4]

    @from_.setter
    def from_(self, from_):
        if self._curr_value < from_:
            self._curr_value = str(from_)
        self.config(from_=from_)

    @property
    def to(self):
        return int(self.config()['to'][4])

    @to.setter
    def to(self, to):
        if self._curr_value > to:
            self._curr_value = str(to)
        self.config(to=to)

    @property
    def values(self):
        return self._values.values

    @values.setter
    def values(self, values):
        self.config(values=values)
        self._values = _ValueList(values, self._match_case)

    @property
    def convert(self):
        return self._convert

    @convert.setter
    def convert(self, convert):
        self._convert = convert

    @property
    def match_case(self):
        return self._match_case

    @match_case.setter
    def match_case(self, match_case):
        self._values.match_case = match_case

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, callback):
        self._callback = callback

    def set(self, value):
        self._var.set(value)
        self._update()

    def validate(self):
        if self._values:
            if self._curr_value in self._values:
                if self._convert > 0:
                    value = self._curr_value.upper()
                elif self._convert < 0:
                    value = self._curr_value.lower()
                else:
                    value = self._curr_value
            else:
                value = self._prev_value
        else:
            if isint(self._curr_value):
                value = int(self._curr_value)
                to = int(self.config()['to'][4])
                from_ = int(self.config()['from'][4])

                if value < from_:
                    value = from_
                elif value > to:
                    value = to
            else:
                value = self._prev_value

        return str(value)
